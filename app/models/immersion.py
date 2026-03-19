from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImmersionScenario(Base):
    __tablename__ = "immersion_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(24), nullable=False, default="beginner")
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RoleplayCharacter(Base):
    __tablename__ = "roleplay_characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("immersion_scenarios.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    personality: Mapped[str] = mapped_column(String(120), nullable=False)
    accent: Mapped[str] = mapped_column(String(80), nullable=False)
    objective: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(24), nullable=False, default="beginner")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ImmersionSession(Base):
    __tablename__ = "immersion_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("immersion_scenarios.id"), nullable=False, index=True)
    character_id: Mapped[int | None] = mapped_column(ForeignKey("roleplay_characters.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    source: Mapped[str] = mapped_column(String(24), nullable=False, default="single")
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_turns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    speaking_speed_wpm: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    filler_words_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    grammar_mistakes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pronunciation_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fluency_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    share_token: Mapped[str | None] = mapped_column(String(48), nullable=True, index=True)


class ImmersionTurn(Base):
    __tablename__ = "immersion_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("immersion_sessions.id"), nullable=False, index=True)
    speaker: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    frequent_errors_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    weak_vocabulary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    pronunciation_gaps_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    avg_speaking_speed_wpm: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    adaptation_state_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )


class ImmersionMission(Base):
    __tablename__ = "immersion_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    required_outcomes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserImmersionMissionProgress(Base):
    __tablename__ = "user_immersion_mission_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("immersion_missions.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    progress_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class MultiplayerChallenge(Base):
    __tablename__ = "multiplayer_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    guest_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("immersion_scenarios.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open")
    winner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    share_token: Mapped[str | None] = mapped_column(String(48), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SmartNotificationQueue(Base):
    __tablename__ = "smart_notification_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    trigger_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
