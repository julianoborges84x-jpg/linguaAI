from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProficiencyLevel(Base):
    __tablename__ = "proficiency_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class LearningTrack(Base):
    __tablename__ = "learning_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cefr_level: Mapped[str] = mapped_column(String(8), index=True)
    target_language_code: Mapped[str] = mapped_column(String(8), index=True, default="en")


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("learning_tracks.id"), index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    competency: Mapped[str] = mapped_column(String(48), index=True)


class LearningUnit(Base):
    __tablename__ = "learning_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("learning_modules.id"), index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cefr_level: Mapped[str] = mapped_column(String(8), index=True)
    learning_objective: Mapped[str] = mapped_column(Text, nullable=False, default="")
    primary_skill: Mapped[str] = mapped_column(String(64), index=True)
    secondary_skill: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prerequisites_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    content_type: Mapped[str] = mapped_column(String(64), nullable=False, default="scenario")
    is_pro_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class LearningObjective(Base):
    __tablename__ = "learning_objectives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("learning_units.id"), index=True)
    objective_text: Mapped[str] = mapped_column(Text, nullable=False)


class SkillTag(Base):
    __tablename__ = "skill_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    estimated_level: Mapped[str] = mapped_column(String(8), nullable=False, default="A1")
    level_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    speaking_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    listening_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vocabulary_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    grammar_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fluency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class LearnerWeakness(Base):
    __tablename__ = "learner_weaknesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_tag: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class LearnerStrength(Base):
    __tablename__ = "learner_strengths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_tag: Mapped[str] = mapped_column(String(64), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class GrammarMastery(Base):
    __tablename__ = "grammar_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    topic: Mapped[str] = mapped_column(String(96), index=True)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="learning")
    last_practiced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    term: Mapped[str] = mapped_column(String(120), index=True)
    translation: Mapped[str] = mapped_column(String(120), nullable=False)
    context: Mapped[str] = mapped_column(String(180), nullable=False, default="general")
    level: Mapped[str] = mapped_column(String(8), index=True, default="A1")
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="general")
    example: Mapped[str] = mapped_column(Text, nullable=False, default="")
    synonyms_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    language_code: Mapped[str] = mapped_column(String(8), index=True, default="en")


class VocabularyProgress(Base):
    __tablename__ = "vocabulary_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_items.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="new")
    ease_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_review_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class MistakeLog(Base):
    __tablename__ = "mistake_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    error_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    user_text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    context_feature: Mapped[str] = mapped_column(String(64), nullable=False, default="chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ReviewQueue(Base):
    __tablename__ = "review_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    queue_type: Mapped[str] = mapped_column(String(48), index=True)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    due_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class LearningUnitProgress(Base):
    __tablename__ = "learning_unit_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("learning_units.id"), index=True)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
