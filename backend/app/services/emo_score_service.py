from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models.emo_score import EmoScore, EmoScoreSource
from typing import Optional


class EmoScoreService:
    """情绪分数评估服务"""

    @staticmethod
    def create_score(
        db: Session,
        user_id: int,
        source: EmoScoreSource,
        stress_score: Optional[int] = None,
        stable_score: Optional[int] = None,
        anxiety_score: Optional[int] = None,
        functional_score: Optional[int] = None,
        session_id: Optional[int] = None
    ) -> EmoScore:
        """
        创建新的情绪评估记录，自动计算变化率

        Args:
            db: 数据库会话
            user_id: 用户 ID
            source: 评估来源 (onboarding/session)
            stress_score: 压力分数 (1-100)
            stable_score: 稳定度分数 (1-100)
            anxiety_score: 焦虑分数 (1-100)
            functional_score: 功能分数 (1-100)
            session_id: 会话 ID（source=SESSION 时必填）

        变化率计算公式: (本次 - 上次) / 上次
        如果上次数据不存在或为 None，则变化率为 None
        """
        # 获取该用户的上一次评估记录（任何来源）
        last_score = (
            db.query(EmoScore)
            .filter(EmoScore.user_id == user_id)
            .order_by(desc(EmoScore.created_at))
            .first()
        )

        # 计算变化率的辅助函数
        def calculate_change(current: Optional[int], previous: Optional[int]) -> Optional[float]:
            if current is None or previous is None or previous == 0:
                return None
            return (current - previous) / previous

        # 计算各项变化率
        if last_score:
            stress_score_change = calculate_change(stress_score, last_score.stress_score)
            stable_score_change = calculate_change(stable_score, last_score.stable_score)
            anxiety_score_change = calculate_change(anxiety_score, last_score.anxiety_score)
            functional_score_change = calculate_change(functional_score, last_score.functional_score)
        else:
            # 第一次评估，无变化率
            stress_score_change = None
            stable_score_change = None
            anxiety_score_change = None
            functional_score_change = None

        # 创建新记录
        new_score = EmoScore(
            user_id=user_id,
            stress_score=stress_score,
            stable_score=stable_score,
            anxiety_score=anxiety_score,
            functional_score=functional_score,
            stress_score_change=stress_score_change,
            stable_score_change=stable_score_change,
            anxiety_score_change=anxiety_score_change,
            functional_score_change=functional_score_change,
            source=source,
            session_id=session_id
        )

        db.add(new_score)
        db.commit()
        db.refresh(new_score)

        return new_score

    @staticmethod
    def get_latest_score(
        db: Session,
        user_id: int,
        source: Optional[EmoScoreSource] = None
    ) -> Optional[EmoScore]:
        """获取用户最新的评估记录"""
        query = db.query(EmoScore).filter(
            EmoScore.user_id == user_id
        )

        if source:
            query = query.filter(EmoScore.source == source)

        return query.order_by(desc(EmoScore.created_at)).first()

    @staticmethod
    def get_score_history(
        db: Session,
        user_id: int,
        source: Optional[EmoScoreSource] = None
    ) -> list[EmoScore]:
        """获取用户的所有评估历史记录"""
        query = db.query(EmoScore).filter(
            EmoScore.user_id == user_id
        )

        if source:
            query = query.filter(EmoScore.source == source)

        query = query.order_by(desc(EmoScore.created_at))

        return query.all()

    @staticmethod
    def get_score_count(
        db: Session,
        user_id: int,
        source: Optional[EmoScoreSource] = None
    ) -> int:
        """获取评估记录总数"""
        query = db.query(EmoScore).filter(
            EmoScore.user_id == user_id
        )

        if source:
            query = query.filter(EmoScore.source == source)

        return query.count()

    @staticmethod
    def get_score_by_id(
        db: Session,
        score_id: int,
        user_id: int
    ) -> Optional[EmoScore]:
        """根据 ID 获取特定评估记录"""
        return db.query(EmoScore).filter(
            EmoScore.id == score_id,
            EmoScore.user_id == user_id
        ).first()
