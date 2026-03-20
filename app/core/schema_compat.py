from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.models.analytics_event import AnalyticsEvent
from app.models.daily_mission import DailyMissionProgress
from app.models.immersion import (
    ImmersionMission,
    ImmersionScenario,
    ImmersionSession,
    ImmersionTurn,
    MultiplayerChallenge,
    RoleplayCharacter,
    SmartNotificationQueue,
    TutorProfile,
    UserImmersionMissionProgress,
)
from app.models.real_life import RealLifeSession, RealLifeTurn
from app.models.daily_challenge import DailyChallengeAttempt
from app.models.pedagogy import (
    GrammarMastery,
    LearnerProfile,
    LearnerStrength,
    LearnerWeakness,
    LearningModule,
    LearningObjective,
    LearningTrack,
    LearningUnit,
    MistakeLog,
    ProficiencyLevel,
    ReviewQueue,
    SkillTag,
    VocabularyItem,
    VocabularyProgress,
    LearningUnitProgress,
)


def ensure_schema_compatibility(engine: Engine, log: Callable[[str], None] | None = None) -> None:
    """
    Runtime safety net for environments with lagging migrations.
    Keeps auth/register working by ensuring required columns/tables exist.
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "users" not in tables:
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    statements: list[str] = []

    if "current_streak" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN current_streak INTEGER NOT NULL DEFAULT 0")
    if "longest_streak" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN longest_streak INTEGER NOT NULL DEFAULT 0")
    if "last_active_date" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN last_active_date DATE NULL")
    if "referral_code" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN referral_code VARCHAR(32) NULL")
    if "referred_by_user_id" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN referred_by_user_id INTEGER NULL")
    if "referred_count" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN referred_count INTEGER NOT NULL DEFAULT 0")
    if "pro_access_until" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN pro_access_until DATE NULL")
    if "voice_messages_used" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN voice_messages_used INTEGER NOT NULL DEFAULT 0")
    if "voice_usage_reset_at" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN voice_usage_reset_at DATE NULL")
    if "google_sub" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN google_sub VARCHAR(255) NULL")
    if "apple_sub" not in user_columns:
        statements.append("ALTER TABLE users ADD COLUMN apple_sub VARCHAR(255) NULL")

    with engine.begin() as connection:
        for stmt in statements:
            connection.execute(text(stmt))
            if log:
                log(f"schema-compat applied: {stmt}")

        dialect = connection.engine.dialect.name.lower()
        if dialect in {"postgresql", "sqlite"}:
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_referral_code ON users (referral_code)"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_sub ON users (google_sub)"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_apple_sub ON users (apple_sub)"))

    # Ensure growth tables exist when migrations have not reached latest revision.
    DailyMissionProgress.__table__.create(bind=engine, checkfirst=True)
    AnalyticsEvent.__table__.create(bind=engine, checkfirst=True)
    ImmersionScenario.__table__.create(bind=engine, checkfirst=True)
    RoleplayCharacter.__table__.create(bind=engine, checkfirst=True)
    ImmersionSession.__table__.create(bind=engine, checkfirst=True)
    ImmersionTurn.__table__.create(bind=engine, checkfirst=True)
    TutorProfile.__table__.create(bind=engine, checkfirst=True)
    ImmersionMission.__table__.create(bind=engine, checkfirst=True)
    UserImmersionMissionProgress.__table__.create(bind=engine, checkfirst=True)
    MultiplayerChallenge.__table__.create(bind=engine, checkfirst=True)
    SmartNotificationQueue.__table__.create(bind=engine, checkfirst=True)
    RealLifeSession.__table__.create(bind=engine, checkfirst=True)
    RealLifeTurn.__table__.create(bind=engine, checkfirst=True)
    DailyChallengeAttempt.__table__.create(bind=engine, checkfirst=True)
    ProficiencyLevel.__table__.create(bind=engine, checkfirst=True)
    LearningTrack.__table__.create(bind=engine, checkfirst=True)
    LearningModule.__table__.create(bind=engine, checkfirst=True)
    LearningUnit.__table__.create(bind=engine, checkfirst=True)
    LearningObjective.__table__.create(bind=engine, checkfirst=True)
    SkillTag.__table__.create(bind=engine, checkfirst=True)
    LearnerProfile.__table__.create(bind=engine, checkfirst=True)
    LearnerWeakness.__table__.create(bind=engine, checkfirst=True)
    LearnerStrength.__table__.create(bind=engine, checkfirst=True)
    GrammarMastery.__table__.create(bind=engine, checkfirst=True)
    VocabularyItem.__table__.create(bind=engine, checkfirst=True)
    VocabularyProgress.__table__.create(bind=engine, checkfirst=True)
    MistakeLog.__table__.create(bind=engine, checkfirst=True)
    ReviewQueue.__table__.create(bind=engine, checkfirst=True)
    LearningUnitProgress.__table__.create(bind=engine, checkfirst=True)

    inspector = inspect(engine)
    tables_after = set(inspector.get_table_names())
    with engine.begin() as connection:
        if "learning_tracks" in tables_after:
            track_cols = {column["name"] for column in inspector.get_columns("learning_tracks")}
            if "target_language_code" not in track_cols:
                connection.execute(text("ALTER TABLE learning_tracks ADD COLUMN target_language_code VARCHAR(8) NOT NULL DEFAULT 'en'"))
                if log:
                    log("schema-compat applied: ALTER TABLE learning_tracks ADD COLUMN target_language_code")
            if connection.engine.dialect.name.lower() in {"postgresql", "sqlite"}:
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_learning_tracks_target_language_code ON learning_tracks (target_language_code)"))

        if "vocabulary_items" in tables_after:
            vocab_cols = {column["name"] for column in inspector.get_columns("vocabulary_items")}
            if "language_code" not in vocab_cols:
                connection.execute(text("ALTER TABLE vocabulary_items ADD COLUMN language_code VARCHAR(8) NOT NULL DEFAULT 'en'"))
                if log:
                    log("schema-compat applied: ALTER TABLE vocabulary_items ADD COLUMN language_code")
            if connection.engine.dialect.name.lower() in {"postgresql", "sqlite"}:
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_vocabulary_items_language_code ON vocabulary_items (language_code)"))

        if "learning_unit_progress" in tables_after and connection.engine.dialect.name.lower() in {"postgresql", "sqlite"}:
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ux_learning_unit_progress_user_unit "
                    "ON learning_unit_progress (user_id, unit_id)"
                )
            )
