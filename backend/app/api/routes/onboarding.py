from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from app.services.database import get_db
from app.models.user import User
from app.models.user_onboarding import UserOnboarding
from app.models.emo_score import EmoScore, EmoScoreSource
from app.models.user_context import UserContext
from app.core.deps import get_current_user
from app.schemas.onboarding import (
    OnboardingStateResponse,
    OnboardingQuestionResponse,
    OnboardingAnswerRequest,
    OnboardingAnswerResponse
)
from app.schemas.emo_score import EmoScoreResponse
from app.agents.onboarding_agent import OnboardingAgentService
import logging

router = APIRouter(tags=["onboarding"])
logger = logging.getLogger(__name__)


@router.get("", response_model=OnboardingStateResponse)
async def get_onboarding_state(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    获取当前 onboarding 状态

    自动处理以下场景：
    1. 已完成 → 返回 is_complete=True
    2. 有未回答问题 → 返回该问题（断点续传）
    3. 全新用户 → 生成第一个问题
    4. 继续中 → 生成下一个问题
    """
    try:
        # 1. 检查是否已完成
        if current_user.has_finished_onboarding:
            logger.info(f"User {current_user.id} already completed onboarding")
            return OnboardingStateResponse(
                is_complete=True,
                session_id=None,
                question=None,
                message="Onboarding already completed"
            )

        # 2. 查询是否有未回答的问题
        unanswered_question = db.query(UserOnboarding)\
            .filter_by(user_id=current_user.id, answered_at=None)\
            .order_by(UserOnboarding.question_number)\
            .first()

        session_id = f"onboarding_user_{current_user.id}"

        # 3. 如果有未回答问题，直接返回（断点续传）
        if unanswered_question:
            logger.info(f"Resume onboarding for user {current_user.id} at question {unanswered_question.question_number}")
            return OnboardingStateResponse(
                is_complete=False,
                session_id=session_id,
                question=OnboardingQuestionResponse(
                    question_number=unanswered_question.question_number,
                    question_text=unanswered_question.question_text,
                    question_type=unanswered_question.question_type,
                    options=unanswered_question.question_options
                ),
                message=f"Resume at question {unanswered_question.question_number}"
            )

        # 4. 全新用户 → 批量生成所有问题
        question_count = db.query(UserOnboarding)\
            .filter_by(user_id=current_user.id)\
            .count()

        if question_count == 0:
            logger.info(f"Batch generate all questions for new user {current_user.id}")

            onboarding_service = OnboardingAgentService()

            prompt = """
请一次性生成 10 个问题，用于了解用户的基本情况。

问题设计要求：
1. 第 1 个：用户称呼（文本输入）
2. 第 2-4 个：咨询目标、主要困扰、压力来源（文本输入）
3. 第 5-7 个：情绪评估 - 焦虑程度、压力水平、情绪稳定性（选择题，2-4个选项）
4. 第 8-10 个：功能评估和补充信息（选择题或文本）

⚠️ **重要：**
- 一次性生成全部 10 个问题
- 选择题必须提供 2-4 个选项，不能超过4个
- 调用 save_multiple_questions 工具保存

请立即生成问题并调用工具。
"""

            response = onboarding_service.agent.run(
                input=prompt,
                user_id=str(current_user.id),
                session_id=session_id,
                session_state={"user_id": current_user.id},
                stream=False
            )

            # 5. 读取第一个问题
            first_question = db.query(UserOnboarding)\
                .filter_by(user_id=current_user.id, question_number=1)\
                .first()

            if first_question:
                return OnboardingStateResponse(
                    is_complete=False,
                    session_id=session_id,
                    question=OnboardingQuestionResponse(
                        question_number=first_question.question_number,
                        question_text=first_question.question_text,
                        question_type=first_question.question_type,
                        options=first_question.question_options
                    ),
                    message="All questions generated"
                )
            else:
                logger.error(f"Failed to generate questions for user {current_user.id}")
                raise HTTPException(500, "Failed to generate questions")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_onboarding_state error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/answer", response_model=OnboardingAnswerResponse)
async def submit_onboarding_answer(
    request: OnboardingAnswerRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    提交答案，返回下一个问题或完成状态
    """
    try:
        if current_user.has_finished_onboarding:
            raise HTTPException(400, "Onboarding already completed")

        # 验证问题是否存在且未回答
        question = db.query(UserOnboarding)\
            .filter_by(
                user_id=current_user.id,
                question_number=request.question_number,
                answered_at=None
            )\
            .first()

        if not question:
            raise HTTPException(400, f"Question {request.question_number} not found or already answered")

        # 2. 保存答案（直接数据库更新，不调用 agent）
        from datetime import datetime
        question.answer = request.answer
        question.answered_at = datetime.utcnow()
        db.commit()

        logger.info(f"User {current_user.id} answered question {request.question_number}")

        # 3. 检查是否还有未回答的问题
        next_question = db.query(UserOnboarding)\
            .filter_by(user_id=current_user.id, answered_at=None)\
            .order_by(UserOnboarding.question_number)\
            .first()

        if next_question:
            # 3.1 还有未回答的问题，直接返回
            return OnboardingAnswerResponse(
                is_complete=False,
                next_question=OnboardingQuestionResponse(
                    question_number=next_question.question_number,
                    question_text=next_question.question_text,
                    question_type=next_question.question_type,
                    options=next_question.question_options
                )
            )

        # 3.2 所有问题已回答 → 调用 agent 生成评分和上下文
        logger.info(f"User {current_user.id} completed all questions, generating assessment")

        # 获取所有回答
        all_answers = db.query(UserOnboarding)\
            .filter_by(user_id=current_user.id)\
            .order_by(UserOnboarding.question_number)\
            .all()

        # 构建提示
        qa_text = "\n\n".join([
            f"问题 {qa.question_number}: {qa.question_text}\n答案: {qa.answer}"
            for qa in all_answers
        ])

        prompt = f"""
用户已完成所有问卷问题，以下是完整的问答记录：

{qa_text}

请基于以上信息，调用 complete_onboarding 工具完成评估：
1. 从第1个问题的答案中提取用户昵称
2. 综合评估 4 个情绪分数（1-100）：
   - stress_score: 压力负荷
   - stable_score: 情绪稳定度
   - anxiety_score: 焦虑指数
   - functional_score: 功能水平
3. 生成用户上下文（Markdown 格式）

请立即调用 complete_onboarding 工具。
"""

        onboarding_service = OnboardingAgentService()

        response = onboarding_service.agent.run(
            input=prompt,
            user_id=str(current_user.id),
            session_id=request.session_id,
            session_state={"user_id": current_user.id},
            stream=False
        )

        # 4. 刷新用户状态
        db.expire_all()  # 清除所有缓存
        current_user = db.query(User).get(current_user.id)  # 重新查询

        if current_user.has_finished_onboarding:
            # 4.1 已完成，返回结果
            logger.info(f"User {current_user.id} completed onboarding")

            emo_score = db.query(EmoScore)\
                .filter_by(user_id=current_user.id, source=EmoScoreSource.ONBOARDING)\
                .order_by(EmoScore.created_at.desc())\
                .first()

            user_context = db.query(UserContext)\
                .filter_by(user_id=current_user.id)\
                .first()

            total_questions = db.query(UserOnboarding)\
                .filter_by(user_id=current_user.id)\
                .count()

            return OnboardingAnswerResponse(
                is_complete=True,
                next_question=None,
                emo_score=EmoScoreResponse.from_orm(emo_score) if emo_score else None,
                user_context=user_context.context_text if user_context else None,
                nickname=current_user.nickname,
                total_questions=total_questions
            )
        else:
            logger.error(f"Failed to complete onboarding for user {current_user.id}")
            raise HTTPException(500, "Failed to complete onboarding")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"submit_onboarding_answer error for user {current_user.id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(500, str(e))
