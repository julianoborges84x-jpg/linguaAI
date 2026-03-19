from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RealLifeSession(Base):
    __tablename__ = "real_life_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    character_role: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    pressure_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    turns_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consecutive_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RealLifeTurn(Base):
    __tablename__ = "real_life_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("real_life_sessions.id"), nullable=False, index=True)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_question: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
