"""
Onboarding Agent Service

负责 onboarding 流程的所有任务：
1. 生成动态问题（5-10 个）
2. 管理问题和答案的持久化
3. 完成后生成 emo_score 和 user_context
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run import RunContext
from app.core.config import settings
from app.db.models.user import User
from app.db.models.user_onboarding import UserOnboarding, QuestionType
from app.db.models.user_context import UserContext
from app.db.models.emo_score import EmoScore, EmoScoreSource
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OnboardingAgentService:
    """Onboarding Agent 服务封装"""

    _instance: Optional['OnboardingAgentService'] = None
    _agent: Optional[Agent] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._agent is not None:
            return

        # 使用与 Therapist 相同的数据库
        from app.agents.therapist_agent_service import TherapistAgentService
        therapist_service = TherapistAgentService()

        # 创建 Onboarding Agent
        self._agent = Agent(
            name="onboarding_agent",
            model=OpenAIChat(
                id=settings.ONBOARDING_MODEL,
                api_key=settings.OPENAI_API_KEY
            ),
            db=therapist_service.agno_db,

            # ===== Memory 配置 =====
            enable_user_memories=False,  # 不需要长期记忆

            # ===== History 配置 =====
            add_history_to_context=True,  # 需要看到之前的问答

            # ===== Tools =====
            tools=[
                self._create_save_multiple_questions_tool(),  # 批量保存问题（主要工具）
                self._create_save_question_tool(),  # 单个保存问题（备用）
                self._create_save_answer_tool(),  # 保存答案（备用，现已不使用）
                self._create_complete_onboarding_tool()  # 完成评估
            ],

            # ===== Instructions =====
            instructions=self._load_onboarding_instructions(),

            markdown=False,
        )

        logger.info("✓ onboarding_agent 初始化完成")

    @property
    def agent(self) -> Agent:
        return self._agent

    # ===== 工具定义 =====

    def _create_save_question_tool(self):
        """创建保存问题的工具"""
        def save_question(
            run_context: RunContext,
            question_text: str,
            question_type: str,  # "choice" or "text"
            options: Optional[List[str]] = None
        ) -> str:
            """
            保存生成的问题

            Args:
                question_text: 问题文本
                question_type: 问题类型 ("choice" 或 "text")
                options: 选择题的选项列表（问答题时为 None）
            """
            # 从 session_state 获取 user_id，从全局获取 db
            user_id = run_context.session_state.get("user_id")

            if not user_id:
                return "错误：缺少用户ID"

            # 重新获取 db session（避免 pickle 问题）
            from app.db.database import SessionLocal
            db = SessionLocal()

            try:
                # 转换为小写并验证 question_type
                question_type_lower = question_type.lower()
                logger.info(f"DEBUG: question_type={question_type} -> question_type_lower={question_type_lower}")
                if question_type_lower not in ["choice", "text"]:
                    return f"错误：question_type 必须是 'choice' 或 'text'，当前值：{question_type}"

                # 验证选择题选项数量
                if question_type_lower == "choice":
                    if not options or len(options) < 2:
                        return "错误：选择题必须提供至少 2 个选项"
                    if len(options) > 4:
                        return f"错误：选择题选项不能超过 4 个（当前 {len(options)} 个），请减少选项后重新生成"

                # 获取当前问题序号
                current_count = db.query(UserOnboarding)\
                    .filter_by(user_id=user_id)\
                    .count()

                # 创建问题
                question = UserOnboarding(
                    user_id=user_id,
                    question_number=current_count + 1,
                    question_text=question_text,
                    question_type=question_type_lower,  # 直接使用字符串值，不转换为 Enum
                    question_options=options,
                    answer=None,
                    answered_at=None
                )
                db.add(question)
                db.commit()

                logger.info(f"✓ 保存问题 {current_count + 1} for user {user_id}: {question_text[:50]}...")
                return f"✓ 问题 {current_count + 1} 已保存"

            except Exception as e:
                logger.error(f"save_question error: {e}")
                db.rollback()
                return f"错误：保存失败 - {str(e)}"
            finally:
                db.close()

        return save_question

    def _create_save_multiple_questions_tool(self):
        """创建批量保存问题的工具"""
        def save_multiple_questions(
            run_context: RunContext,
            questions: List[dict]
        ) -> str:
            """
            批量保存多个问题

            Args:
                questions: 问题列表，每个问题包含：
                    - question_text: 问题文本
                    - question_type: "text" 或 "choice"
                    - options: 选择题选项（问答题时为 null 或空列表）

            Returns:
                成功消息或错误信息
            """
            user_id = run_context.session_state.get("user_id")
            if not user_id:
                return "错误：缺少用户ID"

            # 重新获取 db session（避免 pickle 问题）
            from app.db.database import SessionLocal
            db = SessionLocal()

            try:
                # 验证问题数量
                if not questions or len(questions) < 5:
                    return f"错误：问题数量不足（当前 {len(questions)} 个），至少需要 5 个问题"
                if len(questions) > 10:
                    return f"错误：问题数量过多（当前 {len(questions)} 个），最多 10 个问题"

                # 批量创建问题
                created_questions = []
                for idx, q in enumerate(questions, start=1):
                    question_text = q.get("question_text", "").strip()
                    question_type = q.get("question_type", "").lower()
                    options = q.get("options")

                    # 验证问题文本
                    if not question_text:
                        return f"错误：问题 {idx} 的文本为空"

                    # 验证问题类型
                    if question_type not in ["text", "choice"]:
                        return f"错误：问题 {idx} 的类型无效（{question_type}），必须是 'text' 或 'choice'"

                    # 验证选择题选项
                    if question_type == "choice":
                        if not options or len(options) < 2:
                            return f"错误：问题 {idx} 是选择题但选项少于 2 个"
                        if len(options) > 4:
                            return f"错误：问题 {idx} 的选项超过 4 个（当前 {len(options)} 个），请减少选项"

                    # 创建问题
                    question = UserOnboarding(
                        user_id=user_id,
                        question_number=idx,
                        question_text=question_text,
                        question_type=question_type,
                        question_options=options if question_type == "choice" else None,
                        answer=None,
                        answered_at=None
                    )
                    db.add(question)
                    created_questions.append(f"Q{idx}: {question_text[:30]}...")

                db.commit()

                logger.info(f"✓ 批量保存 {len(questions)} 个问题 for user {user_id}")
                logger.info(f"  问题列表: {', '.join(created_questions)}")
                return f"✓ 成功保存 {len(questions)} 个问题"

            except Exception as e:
                logger.error(f"save_multiple_questions error: {e}")
                db.rollback()
                return f"错误：批量保存失败 - {str(e)}"
            finally:
                db.close()

        return save_multiple_questions

    def _create_save_answer_tool(self):
        """创建保存答案的工具"""
        def save_answer(
            run_context: RunContext,
            question_number: int,
            answer: str
        ) -> str:
            """
            保存用户回答

            Args:
                question_number: 问题序号
                answer: 用户的回答
            """
            user_id = run_context.session_state.get("user_id")

            if not user_id:
                return "错误：缺少用户ID"

            # 重新获取 db session（避免 pickle 问题）
            from app.db.database import SessionLocal
            db = SessionLocal()

            try:
                question = db.query(UserOnboarding)\
                    .filter_by(user_id=user_id, question_number=question_number)\
                    .first()

                if not question:
                    return f"错误：问题 {question_number} 不存在"

                question.answer = answer
                question.answered_at = datetime.utcnow()
                db.commit()

                logger.info(f"✓ 保存回答 {question_number} for user {user_id}: {answer[:50]}...")
                return f"✓ 回答已保存"

            except Exception as e:
                logger.error(f"save_answer error: {e}")
                db.rollback()
                return f"错误：保存失败 - {str(e)}"
            finally:
                db.close()

        return save_answer

    def _create_complete_onboarding_tool(self):
        """创建完成 onboarding 的工具"""
        def complete_onboarding(
            run_context: RunContext,
            nickname: str,
            stress_score: int,
            stable_score: int,
            anxiety_score: int,
            functional_score: int,
            user_context_markdown: str
        ) -> str:
            """
            完成 onboarding，生成 emo_score 和 user_context

            Args:
                nickname: 用户昵称（从第一个问题的回答中提取）
                stress_score: 压力负荷 (1-100)
                stable_score: 情绪稳定度 (1-100)
                anxiety_score: 焦虑指数 (1-100)
                functional_score: 功能水平 (1-100)
                user_context_markdown: 用户上下文（Markdown 格式）
            """
            user_id = run_context.session_state.get("user_id")

            if not user_id:
                return "错误：缺少用户ID"

            # 重新获取 db session（避免 pickle 问题）
            from app.db.database import SessionLocal
            db = SessionLocal()

            try:
                # 1. 保存 emo_score
                emo_score = EmoScore(
                    user_id=user_id,
                    stress_score=stress_score,
                    stable_score=stable_score,
                    anxiety_score=anxiety_score,
                    functional_score=functional_score,
                    source=EmoScoreSource.ONBOARDING,
                    session_id=None
                )
                db.add(emo_score)

                # 2. 保存 user_context
                context = UserContext(
                    user_id=user_id,
                    context_text=user_context_markdown
                )
                db.add(context)

                # 3. 更新用户信息
                user = db.query(User).get(user_id)
                if not user:
                    return "错误：用户不存在"

                user.nickname = nickname
                user.has_finished_onboarding = True

                db.commit()

                logger.info(f"✓ User {user_id} onboarding completed, nickname: {nickname}")
                logger.info(f"  Scores - Stress: {stress_score}, Stable: {stable_score}, "
                          f"Anxiety: {anxiety_score}, Functional: {functional_score}")
                return f"✓ Onboarding 完成！用户昵称：{nickname}"

            except Exception as e:
                db.rollback()
                logger.error(f"complete_onboarding error: {e}")
                return f"错误：{str(e)}"
            finally:
                db.close()

        return complete_onboarding

    def _load_onboarding_instructions(self) -> str:
        """加载 Onboarding 指令"""
        try:
            from app.services.prompt_loader import PromptLoader
            loader = PromptLoader()
            return loader.get_prompt("onboarding_instructions.yaml")
        except Exception as e:
            logger.error(f"Failed to load onboarding instructions: {e}")
            return """你是一位专业的心理咨询引导助手，负责通过智能问答了解用户的基本情况。

请生成 5-10 个动态问题，包括：
1. 用户希望如何被称呼
2. 咨询目标
3. 压力来源
4. 情绪状态
5. 焦虑水平
6. 功能水平

问题类型：
- 开放性话题 → 使用 "text" 类型
- 量化评估 → 使用 "choice" 类型（2-4 个选项）

工具使用：
1. 生成问题后调用 save_question
2. 收到答案后调用 save_answer
3. 收集足够信息后调用 complete_onboarding

在 complete_onboarding 时，需要：
- 提取用户昵称
- 评估 4 个情绪分数（1-100）
- 生成 user_context（Markdown 格式）
"""
