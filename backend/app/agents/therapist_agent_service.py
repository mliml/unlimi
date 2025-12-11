"""
Therapist Agent Service

封装 Agno TherapistAgent 的服务层
"""

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from app.core.config import settings
from app.db.models.user_context import UserContext
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import logging
import threading
from jinja2 import Template

logger = logging.getLogger(__name__)

# 治疗师 prompt 缓存（格式：{user_id: (prompt_text, cached_time)}）
_therapist_prompt_cache: Dict[int, Tuple[str, datetime]] = {}
_cache_lock = threading.Lock()  # 线程锁保护缓存操作


class TherapistAgentService:
    """
    Therapist Agent 服务封装
    负责管理治疗师 AI Agent 的生命周期和交互
    """

    _instance: Optional['TherapistAgentService'] = None
    _agent: Optional[Agent] = None

    def __new__(cls):
        """单例模式，确保全局只有一个 Agent 实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._agent is not None:
            return

        # 初始化 Agno 数据库连接
        if settings.agno_database_url.startswith("postgresql"):
            self.agno_db = PostgresDb(db_url=settings.agno_database_url)
        else:
            # SQLite
            db_file = settings.agno_database_url.replace("sqlite:///", "")
            self.agno_db = SqliteDb(db_file=db_file)

        # 加载基础指令模板（包含 Jinja2 语法）
        self._base_instructions_template = self._load_base_instructions()

        # 创建 Therapist Agent
        self._agent = Agent(
            name="TherapistAgent",
            model=OpenAIChat(
                id=settings.THERAPIST_MODEL,
                api_key=settings.OPENAI_API_KEY
            ),
            db=self.agno_db,

            # ===== Memory 配置 =====
            enable_user_memories=settings.THERAPIST_ENABLE_MEMORY,  # 自动提取用户事实

            # ===== Chat History 配置 =====
            add_history_to_context=True,  # 自动添加历史到上下文
            num_history_runs=settings.THERAPIST_HISTORY_RUNS,  # 根据配置设置

            # ===== Session State 配置 =====
            session_state={},  # 初始为空，运行时动态设置

            # ===== Instructions =====
            # 使用占位符，实际内容通过 session_state 传递
            instructions="""{rendered_base_instructions}

## 治疗师个性化指令

{therapist_prompt}

## 当前用户情况

{user_context}
""",

            # ===== 其他配置 =====
            markdown=settings.THERAPIST_MARKDOWN,
            resolve_in_context=True,  # 在指令中解析变量
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
            db: SQLAlchemy session (用于查询 UserContext 和 Therapist)
            active_duration_seconds: 累计活跃时长（秒）

        Returns:
            AI 回复文本
        """
        try:
            # 1. 加载用户上下文
            user_context = self._load_user_context(user_id, db)

            # 2. 加载治疗师个性化 prompt（带缓存）
            therapist_prompt = self._load_therapist_prompt(user_id, db)

            # 3. 获取 session 对象并更新轮数
            from app.db.models.session import Session as SessionModel
            session_obj = db.query(SessionModel).filter_by(agno_session_id=session_id).first()

            if session_obj:
                # 更新轮数（每次对话往返 +1）
                session_obj.turn_count += 1

                # 判断是否需要提示
                should_remind = self._check_should_remind_timeout(session_obj, db)

                if should_remind:
                    session_obj.overtime_reminder_count += 1

                db.flush()

                active_duration_minutes = session_obj.active_duration_seconds // 60 if session_obj.active_duration_seconds else 0
                turn_count = session_obj.turn_count
            else:
                should_remind = False
                active_duration_minutes = 0
                turn_count = 0

            # 4. 手动渲染 base_instructions 模板（使用 Jinja2）
            from app.core.config import settings
            template_vars = {
                "should_remind_timeout": should_remind,
                "active_duration_minutes": active_duration_minutes,
                "turn_count": turn_count,
                "suggested_duration_minutes": settings.SESSION_SUGGESTED_DURATION_MINUTES,
                "suggested_turns": settings.SESSION_SUGGESTED_TURNS,
            }

            try:
                jinja_template = Template(self._base_instructions_template)
                rendered_base_instructions = jinja_template.render(**template_vars)
                logger.debug(f"Successfully rendered base instructions, length: {len(rendered_base_instructions)}")
            except Exception as e:
                logger.error(f"Failed to render base instructions template: {e}", exc_info=True)
                rendered_base_instructions = self._base_instructions_template  # Fallback to unrendered

            # 5. 构造 session_state
            # 注意：Agno 会自动持久化 session_state，下次运行时会加载
            session_state = {
                "user_context": user_context,
                "therapist_prompt": therapist_prompt,
                "user_id": user_id,
                "rendered_base_instructions": rendered_base_instructions,  # 渲染后的基础指令
                "should_remind_timeout": should_remind,
                "active_duration_minutes": active_duration_minutes,
                "turn_count": turn_count,
                "suggested_duration_minutes": settings.SESSION_SUGGESTED_DURATION_MINUTES,
                "suggested_turns": settings.SESSION_SUGGESTED_TURNS,
            }

            # 6. 调用 Agent
            logger.info(
                f"[THERAPIST_AGENT] user_id={user_id}, session={session_id}, "
                f"duration={active_duration_minutes}min, turns={turn_count}, "
                f"should_remind={should_remind}, message_length={len(message)}"
            )

            # Debug: Log session_state to verify variables are passed
            logger.info(
                f"[THERAPIST_AGENT_STATE] session_state keys: {list(session_state.keys())}, "
                f"should_remind_timeout={session_state.get('should_remind_timeout')}, "
                f"suggested_duration_minutes={session_state.get('suggested_duration_minutes')}, "
                f"suggested_turns={session_state.get('suggested_turns')}"
            )

            # Debug: Log rendered base instructions snippet when timeout reminder is active
            if should_remind and '会话时间管理' in rendered_base_instructions:
                start_idx = rendered_base_instructions.find('会话时间管理')
                snippet = rendered_base_instructions[start_idx:start_idx+400]
                logger.info(f"[THERAPIST_AGENT_RENDERED_BASE] {snippet}")

            response = self._agent.run(
                input=message,
                user_id=str(user_id),  # Agno 使用字符串 user_id
                session_id=session_id,
                session_state=session_state,  # 传递 state
                stream=False
            )

            # Debug: Try to log the rendered instructions
            # Agno Agent should have a way to access the rendered instructions
            try:
                # Check if the agent has rendered instructions available
                if should_remind and hasattr(self._agent, '_get_instructions'):
                    # Try to get the rendered instructions
                    rendered_instructions = self._agent._get_instructions(
                        user_id=str(user_id),
                        session_id=session_id,
                        session_state=session_state
                    )
                    # Log the timeout section
                    if '会话时间管理' in rendered_instructions:
                        start_idx = rendered_instructions.find('会话时间管理')
                        snippet = rendered_instructions[start_idx:start_idx+600]
                        logger.info(f"[THERAPIST_AGENT_RENDERED_INSTRUCTIONS] {snippet}")
            except Exception as debug_e:
                logger.debug(f"Could not retrieve rendered instructions: {debug_e}")

            # Also check the response object
            if hasattr(response, 'messages') and response.messages:
                # Messages are Pydantic objects, not dicts
                system_message = next((m for m in response.messages if hasattr(m, 'role') and m.role == 'system'), None)
                if system_message and hasattr(system_message, 'content'):
                    content = system_message.content or ''
                    logger.info(
                        f"[THERAPIST_AGENT_RESPONSE_SYSTEM] Length: {len(content)}, "
                        f"contains '会话时间管理': {'会话时间管理' in content}"
                    )
                    if should_remind and '会话时间管理' in content:
                        start_idx = content.find('会话时间管理')
                        snippet = content[start_idx:start_idx+600]
                        logger.info(f"[THERAPIST_AGENT_SYSTEM_SNIPPET] {snippet}")

            # 7. 返回回复内容
            return response.content

        except Exception as e:
            logger.error(f"TherapistAgent error: {str(e)}", exc_info=True)
            return "抱歉，我现在遇到了一些问题，请稍后再试。"

    def _load_user_context(self, user_id: int, db: Session) -> str:
        """从数据库加载用户上下文"""
        try:
            ctx = db.query(UserContext).filter_by(user_id=user_id).first()

            if ctx:
                return ctx.context_text
            else:
                return "（用户尚未完成初始评估）"
        except Exception as e:
            logger.error(f"Failed to load user context for user {user_id}: {e}")
            return "（用户信息加载失败）"

    def _load_base_instructions(self) -> str:
        """加载基础治疗师指令"""
        try:
            from app.services.prompt_loader import PromptLoader
            loader = PromptLoader()
            return loader.get_prompt("therapist_base_instructions.yaml")
        except Exception as e:
            logger.error(f"Failed to load therapist instructions: {e}")
            # 返回一个基础的 fallback prompt
            return "你是一位专业的心理咨询师。请以温和、共情的方式回复来访者。"

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

    def _load_therapist_prompt_from_db(self, user_id: int, db: Session) -> str:
        """
        从数据库加载治疗师个性化 prompt（无缓存）

        Args:
            user_id: 用户ID
            db: SQLAlchemy session

        Returns:
            治疗师的个性化 prompt 文本
        """
        try:
            from app.db.models.user import User
            from app.db.models.therapist import Therapist
            from sqlalchemy.orm import joinedload

            # 查询用户及其关联的治疗师（使用 joinedload 优化）
            user = db.query(User).options(
                joinedload(User.therapist)
            ).filter_by(id=user_id).first()

            if not user:
                logger.warning(f"User {user_id} not found")
                return "（用户不存在）"

            if not user.therapist_id:
                logger.warning(f"User {user_id} has no therapist_id assigned")
                return "（未分配治疗师）"

            if not user.therapist:
                logger.warning(f"Therapist {user.therapist_id} not found for user {user_id}")
                return "（治疗师信息未找到）"

            prompt = user.therapist.prompt
            if not prompt or prompt.strip() == "":
                logger.info(f"Therapist {user.therapist_id} has no custom prompt")
                return "（该治疗师暂未设置个性化指令）"

            return prompt

        except Exception as e:
            logger.error(f"Failed to load therapist prompt for user {user_id}: {e}", exc_info=True)
            return "（治疗师指令加载失败）"

    def _load_therapist_prompt(self, user_id: int, db: Session) -> str:
        """
        加载治疗师个性化 prompt（带缓存，线程安全）

        Args:
            user_id: 用户ID
            db: SQLAlchemy session

        Returns:
            治疗师的个性化 prompt 文本
        """
        global _therapist_prompt_cache, _cache_lock

        # 检查缓存（加锁）
        with _cache_lock:
            if user_id in _therapist_prompt_cache:
                cached_prompt, cached_time = _therapist_prompt_cache[user_id]
                # 缓存有效期：5分钟
                if datetime.now() - cached_time < timedelta(minutes=5):
                    logger.debug(f"Using cached therapist prompt for user {user_id}")
                    return cached_prompt

        # 缓存失效或不存在，从数据库加载
        logger.debug(f"Loading therapist prompt from database for user {user_id}")
        prompt = self._load_therapist_prompt_from_db(user_id, db)

        # 更新缓存（加锁）
        with _cache_lock:
            _therapist_prompt_cache[user_id] = (prompt, datetime.now())

        return prompt

    @staticmethod
    def _check_should_remind_timeout(session, db: Session) -> bool:
        """
        判断是否需要提示超时

        Args:
            session: Session 对象
            db: SQLAlchemy session

        Returns:
            是否需要提示
        """
        from app.core.config import settings

        suggested_duration = settings.SESSION_SUGGESTED_DURATION_MINUTES * 60
        suggested_turns = settings.SESSION_SUGGESTED_TURNS
        reminder_interval = settings.SESSION_REMINDER_INTERVAL

        # 未超时则不提示
        if session.active_duration_seconds <= suggested_duration:
            logger.debug(
                f"[TIMEOUT_CHECK] session={session.id}, duration={session.active_duration_seconds}s "
                f"<= suggested={suggested_duration}s, no reminder"
            )
            return False
        if session.turn_count <= suggested_turns:
            logger.debug(
                f"[TIMEOUT_CHECK] session={session.id}, turns={session.turn_count} "
                f"<= suggested={suggested_turns}, no reminder"
            )
            return False

        # 计算超时后经过了多少轮
        overtime_turns = session.turn_count - suggested_turns

        # 间隔提示：第1轮、第4轮、第7轮...（根据配置的间隔）
        if overtime_turns % reminder_interval == 1:
            logger.info(
                f"[TIMEOUT_CHECK] session={session.id}, overtime_turns={overtime_turns}, "
                f"interval={reminder_interval}, WILL REMIND"
            )
            return True

        logger.debug(
            f"[TIMEOUT_CHECK] session={session.id}, overtime_turns={overtime_turns}, "
            f"interval={reminder_interval}, no reminder this turn"
        )
        return False

    @staticmethod
    def clear_therapist_prompt_cache(user_id: int):
        """
        清除指定用户的治疗师 prompt 缓存（线程安全）

        用于用户切换治疗师或开始新会话时，确保使用最新的治疗师信息

        Args:
            user_id: 用户ID
        """
        global _therapist_prompt_cache, _cache_lock

        with _cache_lock:
            if user_id in _therapist_prompt_cache:
                del _therapist_prompt_cache[user_id]
                logger.info(f"Cleared therapist prompt cache for user {user_id}")
