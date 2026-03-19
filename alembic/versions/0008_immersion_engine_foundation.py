"""immersion engine foundation

Revision ID: 0008_immersion_engine_foundation
Revises: 0007_growth_retention_systems
Create Date: 2026-03-17 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0008_immersion_engine_foundation"
down_revision = "0007_growth_retention_systems"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def _create_table_if_missing(name: str, columns: list, fks: list = None, uniques: list = None):
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, name):
        return

    fk_constraints = fks or []
    unique_constraints = uniques or []
    op.create_table(name, *columns, *fk_constraints, *unique_constraints, sa.PrimaryKeyConstraint("id"))


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    _create_table_if_missing(
        "immersion_scenarios",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("difficulty", sa.String(length=24), nullable=False, server_default="beginner"),
            sa.Column("context_json", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        ],
        uniques=[sa.UniqueConstraint("slug")],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "immersion_scenarios"):
        if not _index_exists(inspector, "immersion_scenarios", "ix_immersion_scenarios_id"):
            op.create_index("ix_immersion_scenarios_id", "immersion_scenarios", ["id"])
        if not _index_exists(inspector, "immersion_scenarios", "ix_immersion_scenarios_slug"):
            op.create_index("ix_immersion_scenarios_slug", "immersion_scenarios", ["slug"], unique=True)

    _create_table_if_missing(
        "roleplay_characters",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("scenario_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("personality", sa.String(length=120), nullable=False),
            sa.Column("accent", sa.String(length=80), nullable=False),
            sa.Column("objective", sa.String(length=255), nullable=False),
            sa.Column("difficulty", sa.String(length=24), nullable=False, server_default="beginner"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        ],
        fks=[sa.ForeignKeyConstraint(["scenario_id"], ["immersion_scenarios.id"])],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "roleplay_characters"):
        if not _index_exists(inspector, "roleplay_characters", "ix_roleplay_characters_id"):
            op.create_index("ix_roleplay_characters_id", "roleplay_characters", ["id"])
        if not _index_exists(inspector, "roleplay_characters", "ix_roleplay_characters_scenario_id"):
            op.create_index("ix_roleplay_characters_scenario_id", "roleplay_characters", ["scenario_id"])

    _create_table_if_missing(
        "immersion_sessions",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("scenario_id", sa.Integer(), nullable=False),
            sa.Column("character_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
            sa.Column("source", sa.String(length=24), nullable=False, server_default="single"),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("total_turns", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("speaking_speed_wpm", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("filler_words_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("grammar_mistakes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("pronunciation_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("fluency_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("summary_json", sa.Text(), nullable=True),
            sa.Column("share_token", sa.String(length=48), nullable=True),
        ],
        fks=[
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["scenario_id"], ["immersion_scenarios.id"]),
            sa.ForeignKeyConstraint(["character_id"], ["roleplay_characters.id"]),
        ],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "immersion_sessions"):
        for name, columns in [
            ("ix_immersion_sessions_id", ["id"]),
            ("ix_immersion_sessions_user_id", ["user_id"]),
            ("ix_immersion_sessions_scenario_id", ["scenario_id"]),
            ("ix_immersion_sessions_character_id", ["character_id"]),
            ("ix_immersion_sessions_share_token", ["share_token"]),
        ]:
            if not _index_exists(inspector, "immersion_sessions", name):
                op.create_index(name, "immersion_sessions", columns)

    _create_table_if_missing(
        "immersion_turns",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("session_id", sa.Integer(), nullable=False),
            sa.Column("speaker", sa.String(length=16), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("feedback_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        ],
        fks=[sa.ForeignKeyConstraint(["session_id"], ["immersion_sessions.id"])],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "immersion_turns"):
        if not _index_exists(inspector, "immersion_turns", "ix_immersion_turns_id"):
            op.create_index("ix_immersion_turns_id", "immersion_turns", ["id"])
        if not _index_exists(inspector, "immersion_turns", "ix_immersion_turns_session_id"):
            op.create_index("ix_immersion_turns_session_id", "immersion_turns", ["session_id"])

    _create_table_if_missing(
        "tutor_profiles",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("frequent_errors_json", sa.Text(), nullable=True),
            sa.Column("weak_vocabulary_json", sa.Text(), nullable=True),
            sa.Column("pronunciation_gaps_json", sa.Text(), nullable=True),
            sa.Column("avg_speaking_speed_wpm", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("adaptation_state_json", sa.Text(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        ],
        fks=[sa.ForeignKeyConstraint(["user_id"], ["users.id"])],
        uniques=[sa.UniqueConstraint("user_id")],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "tutor_profiles"):
        if not _index_exists(inspector, "tutor_profiles", "ix_tutor_profiles_id"):
            op.create_index("ix_tutor_profiles_id", "tutor_profiles", ["id"])
        if not _index_exists(inspector, "tutor_profiles", "ix_tutor_profiles_user_id"):
            op.create_index("ix_tutor_profiles_user_id", "tutor_profiles", ["user_id"], unique=True)

    _create_table_if_missing(
        "immersion_missions",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=False),
            sa.Column("scenario_slug", sa.String(length=64), nullable=False),
            sa.Column("required_outcomes_json", sa.Text(), nullable=True),
            sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="120"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        ],
        uniques=[sa.UniqueConstraint("slug")],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "immersion_missions"):
        if not _index_exists(inspector, "immersion_missions", "ix_immersion_missions_id"):
            op.create_index("ix_immersion_missions_id", "immersion_missions", ["id"])
        if not _index_exists(inspector, "immersion_missions", "ix_immersion_missions_slug"):
            op.create_index("ix_immersion_missions_slug", "immersion_missions", ["slug"], unique=True)

    _create_table_if_missing(
        "user_immersion_mission_progress",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("mission_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="pending"),
            sa.Column("progress_json", sa.Text(), nullable=True),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
        ],
        fks=[
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["mission_id"], ["immersion_missions.id"]),
        ],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "user_immersion_mission_progress"):
        if not _index_exists(inspector, "user_immersion_mission_progress", "ix_user_immersion_mission_progress_id"):
            op.create_index("ix_user_immersion_mission_progress_id", "user_immersion_mission_progress", ["id"])
        if not _index_exists(inspector, "user_immersion_mission_progress", "ix_user_immersion_mission_progress_user_id"):
            op.create_index("ix_user_immersion_mission_progress_user_id", "user_immersion_mission_progress", ["user_id"])
        if not _index_exists(inspector, "user_immersion_mission_progress", "ix_user_immersion_mission_progress_mission_id"):
            op.create_index("ix_user_immersion_mission_progress_mission_id", "user_immersion_mission_progress", ["mission_id"])

    _create_table_if_missing(
        "multiplayer_challenges",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("host_user_id", sa.Integer(), nullable=False),
            sa.Column("guest_user_id", sa.Integer(), nullable=True),
            sa.Column("scenario_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="open"),
            sa.Column("winner_user_id", sa.Integer(), nullable=True),
            sa.Column("share_token", sa.String(length=48), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("ended_at", sa.DateTime(), nullable=True),
        ],
        fks=[
            sa.ForeignKeyConstraint(["host_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["guest_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["scenario_id"], ["immersion_scenarios.id"]),
            sa.ForeignKeyConstraint(["winner_user_id"], ["users.id"]),
        ],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "multiplayer_challenges"):
        for name, columns in [
            ("ix_multiplayer_challenges_id", ["id"]),
            ("ix_multiplayer_challenges_host_user_id", ["host_user_id"]),
            ("ix_multiplayer_challenges_guest_user_id", ["guest_user_id"]),
            ("ix_multiplayer_challenges_scenario_id", ["scenario_id"]),
            ("ix_multiplayer_challenges_winner_user_id", ["winner_user_id"]),
            ("ix_multiplayer_challenges_share_token", ["share_token"]),
        ]:
            if not _index_exists(inspector, "multiplayer_challenges", name):
                op.create_index(name, "multiplayer_challenges", columns)

    _create_table_if_missing(
        "smart_notification_queue",
        [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("trigger_type", sa.String(length=64), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="pending"),
            sa.Column("scheduled_for", sa.DateTime(), nullable=False),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
        ],
        fks=[sa.ForeignKeyConstraint(["user_id"], ["users.id"])],
    )
    inspector = inspect(bind)
    if _table_exists(inspector, "smart_notification_queue"):
        if not _index_exists(inspector, "smart_notification_queue", "ix_smart_notification_queue_id"):
            op.create_index("ix_smart_notification_queue_id", "smart_notification_queue", ["id"])
        if not _index_exists(inspector, "smart_notification_queue", "ix_smart_notification_queue_user_id"):
            op.create_index("ix_smart_notification_queue_user_id", "smart_notification_queue", ["user_id"])
        if not _index_exists(inspector, "smart_notification_queue", "ix_smart_notification_queue_trigger_type"):
            op.create_index("ix_smart_notification_queue_trigger_type", "smart_notification_queue", ["trigger_type"])


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = [
        "smart_notification_queue",
        "multiplayer_challenges",
        "user_immersion_mission_progress",
        "immersion_missions",
        "tutor_profiles",
        "immersion_turns",
        "immersion_sessions",
        "roleplay_characters",
        "immersion_scenarios",
    ]
    for table_name in tables:
        inspector = inspect(bind)
        if not _table_exists(inspector, table_name):
            continue
        for idx in inspector.get_indexes(table_name):
            op.drop_index(idx["name"], table_name=table_name)
        op.drop_table(table_name)
