"""
Clerk Agent Service

封装 Agno ClerkAgent 的服务层，负责 onboarding 分析和会话总结
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run import RunContext
from app.core.config import settings
from app.models.user_context import UserContext
from app.models.session_review import SessionReview
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ClerkAgentService:
    """Clerk Agent 服务封装"""

    _instance: Optional['ClerkAgentService'] = None
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

        # 创建 Clerk Agent
        self._agent = Agent(
            name="ClerkAgent",
            model=OpenAIChat(
                id=settings.CLERK_MODEL,
                api_key=settings.OPENAI_API_KEY
            ),
            db=therapist_service.agno_db,

            # ===== Clerk 不需要 Memory =====
            enable_user_memories=False,

            # ===== 但需要访问历史记录 =====
            add_history_to_context=True,  # 自动添加会话历史

            # ===== Tools =====
            tools=[
                self._create_save_user_context_tool(),  # 新增：首次保存用户上下文
                self._create_update_user_context_tool(),
                self._create_save_session_review_tool(),
            ],

            # ===== Instructions =====
            instructions=self._load_clerk_instructions(),

            markdown=False,
        )

        logger.info("✓ ClerkAgent 初始化完成")

    @property
    def agent(self) -> Agent:
        return self._agent

    def analyze_onboarding(
        self,
        user_id: int,
        db: Session
    ) -> Dict:
        """
        分析 onboarding 问卷，生成用户上下文

        该方法替代原 clerk_agent.py 的 analyze_onboarding 功能

        Args:
            user_id: 用户ID
            db: SQLAlchemy session

        Returns:
            {
                "context_text": "Markdown 格式的用户上下文",
                "success": True/False
            }
        """
        try:
            # 1. 读取用户所有 onboarding 问答
            from app.models.user_onboarding import UserOnboarding

            questions = db.query(UserOnboarding)\
                .filter_by(user_id=user_id)\
                .order_by(UserOnboarding.question_number)\
                .all()

            if not questions:
                raise ValueError("No onboarding questions found")

            # 2. 构造问答对话历史
            qa_text = "\n\n".join([
                f"Q{q.question_number}: {q.question_text}\nA: {q.answer or '未回答'}"
                for q in questions
            ])

            # 3. 使用 Agno Agent 分析
            prompt = f"""
请分析以下用户的 onboarding 问答记录，生成结构化的用户上下文（Markdown 格式）。

{qa_text}

要求：
1. 使用以下 Markdown 结构：
   ## 基本信息
   - 昵称：[从第一个问题提取]

   ## 咨询目标
   [用户寻求咨询的主要目的]

   ## 当前状态评估
   - 压力状态：[评估]
   - 情绪稳定性：[评估]
   - 焦虑程度：[评估]
   - 功能水平：[评估]

   ## 关注重点
   [咨询师需要关注的重点事项]

2. 保持简洁专业，每部分 2-5 句话
3. 使用第三人称描述
4. 只输出 Markdown 文本，不要有其他解释

请立即调用 save_user_context 工具保存生成的用户上下文。
"""

            response = self._agent.run(
                input=prompt,
                user_id=str(user_id),
                session_id=f"onboarding_{user_id}",
                session_state={
                    "user_id": user_id
                },
                stream=False
            )

            # 4. 从数据库读取保存的结果
            context = db.query(UserContext).filter_by(user_id=user_id).first()

            if context:
                logger.info(f"✓ User context generated for user {user_id}")
                return {
                    "context_text": context.context_text,
                    "success": True
                }
            else:
                raise ValueError("Failed to save user context")

        except Exception as e:
            logger.error(f"analyze_onboarding error: {e}", exc_info=True)
            return {
                "context_text": None,
                "success": False,
                "error": str(e)
            }

    def process_session_end(
        self,
        user_id: int,
        session_id: int,  # 业务 session ID
        agno_session_id: str,  # Agno session ID
        db: Session
    ) -> Dict:
        """
        会话结束时处理

        Args:
            user_id: 用户ID
            session_id: 业务 session ID (sessions.id)
            agno_session_id: Agno session ID (sessions.agno_session_id)
            db: SQLAlchemy session

        Returns:
            {
                "session_review": "...",
                "key_events": ["...", "..."],
                "context_updated": True/False
            }
        """
        try:
            prompt = """
请完成以下任务：

1. 分析本次咨询对话，生成会话总结：
   - 主要讨论的话题
   - 用户的情绪变化
   - 关键事件（2-5个关键时刻）

2. 判断是否需要更新用户上下文：
   - 如果发现用户的咨询目标、困扰或偏好有变化
   - 或者了解到新的重要信息
   - 则调用 `update_user_context` 工具更新

3. 调用 `save_session_review` 工具保存会话总结和关键事件

请逐步执行。
"""

            logger.info(f"ClerkAgent processing session end for session {session_id}")

            response = self._agent.run(
                input=prompt,
                user_id=str(user_id),
                session_id=agno_session_id,  # 使用 Agno session ID
                session_state={
                    "user_id": user_id,
                    "session_id": session_id  # 传入业务 session ID
                },
                stream=False
            )

            # 从数据库读取保存的结果
            review = db.query(SessionReview).filter_by(session_id=session_id).first()

            if review:
                logger.info(f"✓ Session review saved for session {session_id}")
                return {
                    "session_review": review.message_review,
                    "key_events": review.key_events if review.key_events else [],
                    "context_updated": "update_user_context" in response.content
                }
            else:
                logger.warning(f"Session review not found for session {session_id}")
                return {
                    "session_review": "会话总结生成失败",
                    "key_events": [],
                    "context_updated": False
                }

        except Exception as e:
            logger.error(f"ClerkAgent session end processing failed: {str(e)}", exc_info=True)
            return {
                "session_review": "会话总结生成失败",
                "key_events": [],
                "context_updated": False
            }

    # ===== 工具定义 =====

    def _create_save_user_context_tool(self):
        """创建保存用户上下文的工具（首次创建）"""
        def save_user_context(
            run_context: RunContext,
            context_markdown: str
        ) -> str:
            """
            保存用户上下文（首次创建）

            Args:
                context_markdown: Markdown 格式的用户上下文
            """
            from app.services.database import SessionLocal

            user_id = run_context.session_state.get("user_id")

            if not user_id:
                return "错误：缺少用户ID"

            # 创建独立的 db session（线程安全）
            db = SessionLocal()
            try:
                # 检查是否已存在
                existing = db.query(UserContext).filter_by(user_id=user_id).first()
                if existing:
                    return "错误：用户上下文已存在，请使用 update_user_context"

                # 创建新记录
                context = UserContext(
                    user_id=user_id,
                    context_text=context_markdown
                )
                db.add(context)
                db.commit()

                logger.info(f"✓ 创建用户 {user_id} 的上下文")
                return "✓ 用户上下文已保存"

            except Exception as e:
                logger.error(f"save_user_context error: {e}")
                db.rollback()
                return f"错误：保存失败 - {str(e)}"
            finally:
                db.close()

        return save_user_context

    def _create_update_user_context_tool(self):
        """创建更新用户上下文的工具"""
        def update_user_context(
            run_context: RunContext,
            new_context_markdown: str
        ) -> str:
            """
            更新用户上下文

            Args:
                new_context_markdown: 新的用户上下文（完整替换）
            """
            from app.services.database import SessionLocal

            user_id = run_context.session_state.get("user_id")

            if not user_id:
                return "错误：缺少用户ID"

            # 创建独立的 db session（线程安全）
            db = SessionLocal()
            try:
                ctx = db.query(UserContext).filter_by(user_id=user_id).first()

                if not ctx:
                    return "错误：用户上下文不存在，请先完成 onboarding"

                # 更新
                ctx.context_text = new_context_markdown
                ctx.updated_at = datetime.utcnow()
                db.commit()

                logger.info(f"✓ 更新用户 {user_id} 的上下文")
                return "✓ 用户上下文已更新"

            except Exception as e:
                logger.error(f"update_user_context error: {e}")
                db.rollback()
                return f"错误：更新失败 - {str(e)}"
            finally:
                db.close()

        return update_user_context

    def _create_save_session_review_tool(self):
        """创建保存会话总结的工具"""
        def save_session_review(
            run_context: RunContext,
            session_review: str,
            key_events: List[str]
        ) -> str:
            """
            保存会话总结

            Args:
                session_review: 会话总结文本
                key_events: 关键事件列表（字符串数组）
            """
            from app.services.database import SessionLocal

            session_id = run_context.session_state.get("session_id")

            if not session_id:
                return "错误：缺少会话ID"

            # 创建独立的 db session（线程安全）
            db = SessionLocal()
            try:
                review = SessionReview(
                    session_id=session_id,
                    message_review=session_review,
                    key_events=key_events
                )
                db.add(review)
                db.commit()

                logger.info(f"✓ 保存会话 {session_id} 的总结")
                return f"✓ 会话总结已保存（{len(key_events)} 个关键事件）"

            except Exception as e:
                logger.error(f"save_session_review error: {e}")
                db.rollback()
                return f"错误：保存失败 - {str(e)}"
            finally:
                db.close()

        return save_session_review

    def _load_clerk_instructions(self) -> str:
        """加载 Clerk 指令"""
        try:
            from app.services.prompt_loader import PromptLoader
            loader = PromptLoader()
            return loader.get_prompt("clerk_base_instructions.yaml")
        except Exception as e:
            logger.error(f"Failed to load clerk instructions: {e}")
            return "你是一位心理咨询助理，负责处理咨询的行政和分析工作。"
