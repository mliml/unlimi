import logging
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.agents.therapist_agent_service import TherapistAgentService
from app.agents.clerk_agent_service import ClerkAgentService
from app.agents.intent_classifier import IntentClassifier  # 保留但暂时不使用
from app.db.models.session import Session as SessionModel

logger = logging.getLogger(__name__)


class SessionOrchestrator:
    """
    Orchestrates the session flow and coordinates agents.
    Manages conversation context and agent interactions with Agno framework.
    """

    def __init__(self, db: Session):
        """
        Initialize session orchestrator.

        Args:
            db: Database session
        """
        self.db = db
        self.therapist_service = TherapistAgentService()
        self.clerk_service = ClerkAgentService()
        # self.intent_classifier = IntentClassifier(llm_service)  # 暂停使用

    def process_message(
        self,
        user_id: int,
        session_id: int,
        agno_session_id: str,
        user_message: str,
        active_duration_seconds: Optional[int] = None
    ) -> str:
        """
        Process a user message and generate a therapeutic response.

        Args:
            user_id: User ID
            session_id: Business session ID (sessions.id)
            agno_session_id: Agno session ID (sessions.agno_session_id)
            user_message: User's message text
            active_duration_seconds: Accumulated active duration in seconds (from frontend)

        Returns:
            Therapist's response

        Raises:
            ValueError: If user context not found
            Exception: If processing fails
        """
        try:
            logger.info(f"Processing message for user {user_id}, session {session_id}")

            # 直接调用 TherapistAgentService
            # 不再需要手动加载 history 和 prompt，Agno 会自动处理
            response = self.therapist_service.chat(
                user_id=user_id,
                session_id=agno_session_id,  # 使用 Agno session ID
                message=user_message,
                db=self.db,
                active_duration_seconds=active_duration_seconds
            )

            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise Exception(f"Error processing message: {str(e)}")

    def end_session_with_review(
        self,
        user_id: int,
        session_id: int,
        agno_session_id: str
    ) -> Dict:
        """
        End session and generate review summary using ClerkAgent.

        Args:
            user_id: User ID
            session_id: Business session ID (sessions.id)
            agno_session_id: Agno session ID (sessions.agno_session_id)

        Returns:
            Dictionary containing:
            - session_review: str
            - key_events: List[str]
            - context_updated: bool

        Raises:
            Exception: If processing fails
        """
        try:
            logger.info(f"Ending session {session_id} with review")

            # 调用 ClerkAgentService 处理会话结束
            # ClerkAgent 会自动从 Agno 加载会话历史
            result = self.clerk_service.process_session_end(
                user_id=user_id,
                session_id=session_id,
                agno_session_id=agno_session_id,
                db=self.db
            )

            logger.info(
                f"Session {session_id} review generated: "
                f"review_length={len(result['session_review'])}, "
                f"key_events_count={len(result['key_events'])}"
            )

            return result

        except Exception as e:
            logger.error(f"Error ending session with review: {str(e)}", exc_info=True)
            raise Exception(f"Error ending session with review: {str(e)}")
