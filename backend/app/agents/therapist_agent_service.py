"""
Therapist Agent Service

封装 Agno TherapistAgent 的服务层（极简优化版）
"""

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from app.core.config import settings
from app.core.openai_logger import create_logging_http_client, openai_logging_context
from app.models.user_context import UserContext
from app.services.session_timeout_service import SessionTimeoutService
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class TherapistAgentService:
    """
    Therapist Agent 服务封装
    负责管理治疗师 AI Agent 的生命周期和交互
    """

    def __init__(self):
        # 初始化 Agno 数据库连接
        if settings.agno_database_url.startswith("postgresql"):
            self.agno_db = PostgresDb(db_url=settings.agno_database_url)
        else:
            # SQLite
            db_file = settings.agno_database_url.replace("sqlite:///", "")
            self.agno_db = SqliteDb(db_file=db_file)

        # 创建带日志功能的 HTTP client（用于记录 admin 用户的 prompts）
        logging_http_client = create_logging_http_client()

        # 创建 Therapist Agent
        self._agent = Agent(
            name="TherapistAgent",
            model=OpenAIChat(
                id=settings.THERAPIST_MODEL,
                api_key=settings.OPENAI_API_KEY,
                http_client=logging_http_client  # 使用自定义 HTTP client
            ),
            db=self.agno_db,

            # ===== Memory 配置 =====
            enable_user_memories=settings.THERAPIST_ENABLE_MEMORY,  # 自动提取用户事实

            # ===== Chat History 配置 =====
            add_history_to_context=True,  # 自动添加历史到上下文
            num_history_runs=settings.THERAPIST_HISTORY_RUNS,

            # ===== Instructions =====
            instructions="{instructions}",  # 通过 session_state 传递

            # ===== 其他配置 =====
            markdown=settings.THERAPIST_MARKDOWN,
        )

        logger.info("✓ TherapistAgent 初始化完成")

    @property
    def agent(self) -> Agent:
        """获取 Agent 实例"""
        return self._agent

    def chat(
        self,
        user_id: int,
        session_id: str,
        message: str,
        db: Session,
        active_duration_seconds: Optional[int] = None
    ) -> str:
        """
        处理用户消息

        Args:
            user_id: 用户ID
            session_id: 会话ID（Agno session ID）
            message: 用户消息
            db: SQLAlchemy session
            active_duration_seconds: 累计活跃时长（秒）

        Returns:
            AI 回复文本
        """
        try:
            # 1. 查询用户信息
            from app.models.user import User
            user = db.query(User).filter_by(id=user_id).first()
            is_admin = user.is_admin if user else False

            # 2. 加载数据
            user_context = self._load_user_context(user_id, db)
            therapist_prompt = self._load_therapist_prompt(user_id, db)

            # 3. 检查超时
            from app.models.session import Session as SessionModel
            session_obj = db.query(SessionModel).filter_by(agno_session_id=session_id).first()
            timeout_info = SessionTimeoutService.check_and_update(session_obj, db)

            # 4. 构建指令（两种模式：normal vs timeout）
            if timeout_info["should_remind"]:
                timeout_reminder = self._load_timeout_reminder()
                instructions = f"{therapist_prompt}\n\n{timeout_reminder}\n\n## 当前用户情况\n\n{user_context}"
            else:
                instructions = f"{therapist_prompt}\n\n## 当前用户情况\n\n{user_context}"

            # 5. 调用 Agent
            logger.info(
                f"[THERAPIST] user={user_id}, session={session_id}, "
                f"timeout={timeout_info['should_remind']}, admin={is_admin}"
            )

            with openai_logging_context(user_id=user_id, session_id=session_id, is_admin=is_admin):
                response = self._agent.run(
                    input=message,
                    user_id=str(user_id),
                    session_id=session_id,
                    session_state={"instructions": instructions},
                    stream=False
                )

            return response.content

        except Exception as e:
            logger.error(f"TherapistAgent error: {e}", exc_info=True)
            return "抱歉，我现在遇到了一些问题，请稍后再试。"

    def _load_user_context(self, user_id: int, db: Session) -> str:
        """从数据库加载用户上下文"""
        try:
            ctx = db.query(UserContext).filter_by(user_id=user_id).first()
            return ctx.context_text if ctx else "（用户尚未完成初始评估）"
        except Exception as e:
            logger.error(f"Failed to load user context for user {user_id}: {e}")
            return "（用户信息加载失败）"

    def _load_therapist_prompt(self, user_id: int, db: Session) -> str:
        """从数据库加载治疗师个性化 prompt"""
        try:
            from app.models.user import User
            from sqlalchemy.orm import joinedload

            user = db.query(User).options(joinedload(User.therapist)).filter_by(id=user_id).first()

            if not user:
                logger.warning(f"User {user_id} not found")
                return "（用户不存在）"

            if not user.therapist_id or not user.therapist:
                logger.warning(f"User {user_id} has no therapist assigned")
                return "（未分配治疗师）"

            prompt = user.therapist.prompt
            if not prompt or prompt.strip() == "":
                logger.info(f"Therapist {user.therapist_id} has no custom prompt")
                return "（该治疗师暂未设置个性化指令）"

            return prompt

        except Exception as e:
            logger.error(f"Failed to load therapist prompt for user {user_id}: {e}", exc_info=True)
            return "（治疗师指令加载失败）"

    def _load_timeout_reminder(self) -> str:
        """加载超时提示文本"""
        try:
            from app.services.prompt_loader import PromptLoader
            loader = PromptLoader()
            return loader.get_prompt("therapist_timeout.yaml")
        except Exception as e:
            logger.error(f"Failed to load timeout reminder: {e}")
            return "## ⚠️ 重要提示\n\n本次咨询时间已经比较长了。"

    def get_user_memories(self, user_id: int) -> List[Dict]:
        """
        获取用户的所有记忆（用于前端展示）

        Returns:
            [
                {
                    "memory": "用户喜欢户外活动",
                    "topics": ["interests"],
                    "created_at": "2025-12-08T10:00:00",
                    "updated_at": "2025-12-08T10:00:00",
                    "memory_id": "xxx"
                },
                ...
            ]
        """
        try:
            memories = self._agent.get_user_memories(user_id=str(user_id))

            return [
                {
                    "memory_id": m.memory_id,
                    "memory": m.memory,
                    "topics": m.topics if m.topics else [],
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "updated_at": m.updated_at.isoformat() if m.updated_at else None,
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get user memories for user {user_id}: {e}")
            return []
