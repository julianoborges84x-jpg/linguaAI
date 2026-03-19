from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DailyChallengeAttempt(Base):
    __tablename__ = "daily_challenge_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    day_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False)
    challenge_title: Mapped[str] = mapped_column(String(128), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    real_life_session_id: Mapped[int | None] = mapped_column(ForeignKey("real_life_sessions.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    penalty_applied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    badge_awarded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
