from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, desc, text
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.deps import get_current_user
from app.db.models.user import User
from app.db.models.session import Session, SessionStatus
from app.schemas.session_action import SessionStartResponse, SessionEndResponse, ActiveSessionResponse
from app.schemas.session_message import SessionMessageRequest, SessionMessageResponse, SessionMessageListItem
from app.schemas.session import SessionDetail, SessionHistoryItem
from app.orchestrator.session_orchestrator import SessionOrchestrator
from app.agents.therapist_agent_service import TherapistAgentService
import logging

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)


@router.get("/active", response_model=ActiveSessionResponse)
def get_active_session(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Check if current user has an active (open) session.
    """
    active_session = db.query(Session).filter(
        Session.user_id == current_user.id,
        Session.status == SessionStatus.open
    ).order_by(
        desc(Session.start_time)
    ).first()

    if active_session:
        return ActiveSessionResponse(
            active=True,
            session_id=active_session.id
        )
    else:
        return ActiveSessionResponse(
            active=False,
            session_id=None
        )


@router.get("/history", response_model=List[SessionHistoryItem])
def get_history_sessions(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get list of all closed sessions for the current user.

    Note: Message count is calculated from Agno's agno_sessions.runs JSONB field.
    """
    try:
        # 查询已关闭的 sessions
        sessions = db.query(Session).filter(
            Session.user_id == current_user.id,
            Session.status == SessionStatus.closed
        ).order_by(
            Session.start_time.asc()
        ).all()

        result = []
        for idx, session in enumerate(sessions, start=1):
            # 从 Agno 表的 runs 字段计算消息数量
            message_count = 0
            if session.agno_session_id:
                try:
                    # 查询 runs 数组长度，每个 run 包含 1 对用户消息和助手回复
                    count_query = text("""
                        SELECT jsonb_array_length(runs) as run_count
                        FROM ai.agno_sessions
                        WHERE session_id = :session_id
                    """)
                    count_result = db.execute(count_query, {"session_id": session.agno_session_id})
                    row = count_result.fetchone()
                    # 每个 run 包含 1 个用户消息 + 1 个助手回复 = 2 条消息
                    message_count = (row.run_count * 2) if row and row.run_count else 0
                except Exception as e:
                    logger.warning(f"Failed to count messages for session {session.id}: {e}")
                    message_count = 0

            result.append(SessionHistoryItem(
                id=session.id,
                start_time=session.start_time,
                end_time=session.end_time,
                message_count=message_count,
                index=idx
            ))

        return result

    except Exception as e:
        logger.error(f"Failed to fetch session history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch session history: {str(e)}")


@router.get("/{session_id}", response_model=SessionDetail)
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get detailed information about a specific session.
    """
    # Validate session exists and belongs to user
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session"
        )

    # Get message count from Agno runs
    message_count = 0
    if session.agno_session_id:
        try:
            # 查询 runs 数组长度，每个 run 包含 1 对用户消息和助手回复
            count_query = text("""
                SELECT jsonb_array_length(runs) as run_count
                FROM ai.agno_sessions
                WHERE session_id = :session_id
            """)
            count_result = db.execute(count_query, {"session_id": session.agno_session_id})
            row = count_result.fetchone()
            # 每个 run 包含 1 个用户消息 + 1 个助手回复 = 2 条消息
            message_count = (row.run_count * 2) if row and row.run_count else 0
        except Exception as e:
            logger.warning(f"Failed to count messages for session {session_id}: {e}")

    # Calculate should_remind for active sessions
    from app.agents.therapist_agent_service import TherapistAgentService
    should_remind = False
    if session.status == SessionStatus.open:
        should_remind = TherapistAgentService._check_should_remind_timeout(session, db)

    return SessionDetail(
        id=session.id,
        start_time=session.start_time,
        end_time=session.end_time,
        is_closed=(session.status == SessionStatus.closed),
        message_count=message_count,
        review_text=session.review.message_review if session.review else None,
        key_events=session.review.key_events if session.review else [],
        plan_text=None,
        # Session timing and turn control
        active_duration_seconds=session.active_duration_seconds,
        turn_count=session.turn_count,
        overtime_reminder_count=session.overtime_reminder_count,
        should_remind=should_remind
    )


@router.post("/start", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Start a new therapy session.

    Creates a new session with agno_session_id and generates therapist's opening message.

    Important: When starting a new session, all previous open sessions for this user
    will be automatically closed to ensure only one active session at a time.
    """
    try:
        # Close all previous open sessions for this user that are older than 24 hours
        # This prevents accidentally closing sessions in other tabs
        timeout = timedelta(hours=24)
        cutoff_time = datetime.utcnow() - timeout

        previous_open_sessions = db.query(Session).filter(
            Session.user_id == current_user.id,
            Session.status == SessionStatus.open,
            Session.start_time < cutoff_time
        ).all()

        if previous_open_sessions:
            logger.info(f"Closing {len(previous_open_sessions)} previous open session(s) older than 24 hours for user {current_user.id}")
            for session in previous_open_sessions:
                session.status = SessionStatus.closed
                session.end_time = datetime.utcnow()
            db.flush()

        # Check if user already has an active session (within 24 hours)
        active_session = db.query(Session).filter(
            Session.user_id == current_user.id,
            Session.status == SessionStatus.open
        ).first()

        if active_session:
            logger.warning(f"User {current_user.id} already has an active session {active_session.id}, force-closing it")
            active_session.status = SessionStatus.closed
            active_session.end_time = datetime.utcnow()
            db.flush()

        # Create new session
        new_session = Session(
            user_id=current_user.id,
            status=SessionStatus.open
        )
        db.add(new_session)
        db.flush()  # Get session.id

        # Generate agno_session_id
        timestamp = int(datetime.utcnow().timestamp())
        new_session.agno_session_id = f"session_{new_session.id}_{timestamp}"

        db.commit()
        db.refresh(new_session)

        logger.info(f"Created session {new_session.id} with agno_session_id: {new_session.agno_session_id}")

        # Clear therapist prompt cache to ensure latest therapist info is used
        # This is important when user switches therapist
        TherapistAgentService.clear_therapist_prompt_cache(current_user.id)

        # Auto-generate therapist's opening message
        try:
            orchestrator = SessionOrchestrator(db=db)
            opening_message = orchestrator.process_message(
                user_id=current_user.id,
                session_id=new_session.id,
                agno_session_id=new_session.agno_session_id,
                user_message="开始咨询"  # System trigger message
            )
            logger.info(f"Generated opening message for session {new_session.id}")
        except Exception as e:
            # If opening message generation fails, log error but don't fail session creation
            logger.error(f"Failed to generate opening message for session {new_session.id}: {e}", exc_info=True)

        # Commit turn_count update from opening message
        db.commit()

        return SessionStartResponse(session_id=new_session.id)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to start session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.get("/{session_id}/get_messages", response_model=List[SessionMessageListItem])
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get all messages for a specific session from Agno.
    """
    # Validate session
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session"
        )

    if not session.agno_session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not migrated to Agno yet"
        )

    # Fetch messages from Agno
    try:
        # Query agno_sessions table directly for runs
        query = text("""
            SELECT runs FROM ai.agno_sessions
            WHERE session_id = :session_id
        """)

        result = db.execute(query, {"session_id": session.agno_session_id})
        row = result.fetchone()

        if not row or not row.runs:
            # No messages yet
            return []

        runs = row.runs

        # Convert runs to message list
        messages = []
        msg_id = 0

        for run in runs:
            # Add user message
            if "input" in run and "input_content" in run["input"]:
                messages.append(SessionMessageListItem(
                    id=msg_id,
                    sender="user",
                    message=run["input"]["input_content"],
                    created_at=run.get("created_at", 0)
                ))
                msg_id += 1

            # Add assistant message
            if "content" in run:
                messages.append(SessionMessageListItem(
                    id=msg_id,
                    sender="assistant",
                    message=run["content"],
                    created_at=run.get("created_at", 0)
                ))
                msg_id += 1

        # Filter out system trigger message "开始咨询"
        messages = [msg for msg in messages if not (msg.sender == "user" and msg.message == "开始咨询")]

        # Re-index message IDs after filtering
        for idx, msg in enumerate(messages):
            msg.id = idx

        return messages

    except Exception as e:
        logger.error(f"Failed to fetch messages for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )


@router.post("/{session_id}/post_message", response_model=SessionMessageResponse)
def send_message(
    session_id: int,
    message_request: SessionMessageRequest,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Send a message in a therapy session and get therapist's response.

    Messages are automatically stored by Agno framework.
    """
    try:
        # Validate session
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this session"
            )

        if session.status != SessionStatus.open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is closed"
            )

        # Log incoming request
        logger.info(
            f"[POST_MESSAGE] session_id={session_id}, user_id={current_user.id}, "
            f"active_duration={message_request.active_duration_seconds}s, "
            f"message_length={len(message_request.message)}"
        )

        # Update session active duration if provided by frontend
        if message_request.active_duration_seconds is not None:
            session.active_duration_seconds = message_request.active_duration_seconds
            db.flush()

        # Process message with orchestrator
        orchestrator = SessionOrchestrator(db=db)

        try:
            therapist_reply = orchestrator.process_message(
                user_id=current_user.id,
                session_id=session.id,
                agno_session_id=session.agno_session_id,
                user_message=message_request.message,
                active_duration_seconds=message_request.active_duration_seconds
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate response: {str(e)}"
            )

        # Log success with updated session state
        logger.info(
            f"[POST_MESSAGE_SUCCESS] session_id={session_id}, "
            f"turn_count={session.turn_count}, "
            f"overtime_reminder_count={session.overtime_reminder_count}"
        )

        # Commit all changes (turn_count, active_duration_seconds, overtime_reminder_count)
        db.commit()

        return SessionMessageResponse(reply=therapist_reply)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/{session_id}/end", response_model=SessionEndResponse)
def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    End a therapy session and generate AI-powered summary.

    Uses ClerkAgent to analyze the session and generate review.
    """
    try:
        # Validate session
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this session"
            )

        if session.status == SessionStatus.closed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is already closed"
            )

        # Process session with ClerkAgent
        orchestrator = SessionOrchestrator(db=db)

        try:
            result = orchestrator.end_session_with_review(
                user_id=current_user.id,
                session_id=session.id,
                agno_session_id=session.agno_session_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate session review: {str(e)}"
            )

        # Update session status
        session.status = SessionStatus.closed
        session.end_time = datetime.utcnow()
        db.commit()

        logger.info(f"Session {session_id} ended successfully")

        return SessionEndResponse(
            session_id=session.id,
            session_review=result["session_review"],
            key_events=result.get("key_events", [])
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to end session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )
