"""
Session Timeout Service

极简的会话超时管理服务
"""

from app.models.session import Session
from app.core.config import settings
from sqlalchemy.orm import Session as DBSession
import logging

logger = logging.getLogger(__name__)


class SessionTimeoutService:
    """会话超时管理服务（极简版）"""

    @staticmethod
    def check_and_update(session: Session, db: DBSession) -> dict:
        """
        检查超时状态并更新会话

        Args:
            session: Session 对象
            db: 数据库 session

        Returns:
            {"should_remind": bool}
        """
        if not session:
            return {"should_remind": False}

        # 更新轮数
        session.turn_count += 1

        # 检查是否超时（只判断时长）
        suggested_duration = settings.SESSION_SUGGESTED_DURATION_MINUTES * 60
        should_remind = session.active_duration_seconds > suggested_duration

        # 持久化
        db.flush()

        logger.info(
            f"[SESSION] id={session.id}, turns={session.turn_count}, "
            f"duration={session.active_duration_seconds}s, timeout={should_remind}"
        )

        return {"should_remind": should_remind}
