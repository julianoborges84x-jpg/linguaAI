"""real life mode

Revision ID: 0009_real_life_mode
Revises: 0008_immersion_engine_foundation
Create Date: 2026-03-17 00:10:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0009_real_life_mode"
down_revision = "0008_immersion_engine_foundation"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _table_exists(inspector, "real_life_sessions"):
        op.create_table(
            "real_life_sessions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("scenario", sa.String(length=64), nullable=False),
            sa.Column("character_role", sa.String(length=80), nullable=False),
            sa.Column("difficulty_level", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("pressure_seconds", sa.Integer(), nullable=False, server_default="30"),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
            sa.Column("turns_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("consecutive_correct", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = inspect(bind)
    if _table_exists(inspector, "real_life_sessions"):
        for name, columns in [
            ("ix_real_life_sessions_id", ["id"]),
            ("ix_real_life_sessions_user_id", ["user_id"]),
            ("ix_real_life_sessions_scenario", ["scenario"]),
        ]:
            if not _index_exists(inspector, "real_life_sessions", name):
                op.create_index(name, "real_life_sessions", columns)

    inspector = inspect(bind)
    if not _table_exists(inspector, "real_life_turns"):
        op.create_table(
            "real_life_turns",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("session_id", sa.Integer(), nullable=False),
            sa.Column("user_message", sa.Text(), nullable=False),
            sa.Column("ai_question", sa.Text(), nullable=False),
            sa.Column("feedback_json", sa.Text(), nullable=True),
            sa.Column("response_time_seconds", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_correct", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["session_id"], ["real_life_sessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = inspect(bind)
    if _table_exists(inspector, "real_life_turns"):
        for name, columns in [
            ("ix_real_life_turns_id", ["id"]),
            ("ix_real_life_turns_session_id", ["session_id"]),
        ]:
            if not _index_exists(inspector, "real_life_turns", name):
                op.create_index(name, "real_life_turns", columns)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "real_life_turns"):
        for idx in inspector.get_indexes("real_life_turns"):
            op.drop_index(idx["name"], table_name="real_life_turns")
        op.drop_table("real_life_turns")

    inspector = inspect(bind)
    if _table_exists(inspector, "real_life_sessions"):
        for idx in inspector.get_indexes("real_life_sessions"):
            op.drop_index(idx["name"], table_name="real_life_sessions")
        op.drop_table("real_life_sessions")
