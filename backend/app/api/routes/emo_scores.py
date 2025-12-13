from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.services.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.session import Session
from app.models.emo_score import EmoScoreSource
from app.schemas.emo_score import (
    EmoScoreCreate,
    EmoScoreResponse,
    EmoScoreListResponse
)
from app.services.emo_score_service import EmoScoreService

router = APIRouter(prefix="/emo-score", tags=["emo-score"])


@router.post("/", response_model=EmoScoreResponse, status_code=201)
def create_emo_score(
    data: EmoScoreCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的情绪评估记录

    - 自动计算相对上次评估的变化率
    - 如果 source=session，必须提供 session_id
    """
    # 验证：如果 source=session，必须提供 session_id
    if data.source == EmoScoreSource.SESSION and not data.session_id:
        raise HTTPException(
            status_code=400,
            detail="当评估来源为 session 时，必须提供 session_id"
        )

    # 验证：session_id 必须属于当前用户
    if data.session_id:
        session = db.query(Session).filter(
            Session.id == data.session_id,
            Session.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或不属于当前用户")

    score = EmoScoreService.create_score(
        db=db,
        user_id=current_user.id,
        source=data.source,
        stress_score=data.stress_score,
        stable_score=data.stable_score,
        anxiety_score=data.anxiety_score,
        functional_score=data.functional_score,
        session_id=data.session_id
    )

    return score


@router.get("/latest", response_model=EmoScoreResponse)
def get_latest_emo_score(
    source: Optional[EmoScoreSource] = Query(None, description="筛选评估来源"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户最新的情绪评估记录

    - 可选参数 source 用于筛选特定来源的最新评估
    """
    score = EmoScoreService.get_latest_score(
        db=db,
        user_id=current_user.id,
        source=source
    )

    if not score:
        raise HTTPException(status_code=404, detail="未找到评估记录")

    return score


@router.get("/list", response_model=EmoScoreListResponse)
def get_emo_score_list(
    source: Optional[EmoScoreSource] = Query(None, description="筛选评估来源"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有情绪评估历史记录

    - 可按来源筛选
    - 按创建时间倒序排列
    """
    total = EmoScoreService.get_score_count(
        db=db,
        user_id=current_user.id,
        source=source
    )

    items = EmoScoreService.get_score_history(
        db=db,
        user_id=current_user.id,
        source=source
    )

    return {
        "total": total,
        "items": items
    }


@router.get("/{score_id}", response_model=EmoScoreResponse)
def get_emo_score_by_id(
    score_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据 ID 获取特定的评估记录
    """
    score = EmoScoreService.get_score_by_id(
        db=db,
        score_id=score_id,
        user_id=current_user.id
    )

    if not score:
        raise HTTPException(status_code=404, detail="评估记录不存在")

    return score
