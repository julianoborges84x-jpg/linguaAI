"""daily challenge mode

Revision ID: 0010_daily_challenge_mode
Revises: 0009_real_life_mode
Create Date: 2026-03-17 00:20:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0010_daily_challenge_mode"
down_revision = "0009_real_life_mode"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _table_exists(inspector, "daily_challenge_attempts"):
        op.create_table(
            "daily_challenge_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("day_date", sa.Date(), nullable=False),
            sa.Column("scenario", sa.String(length=64), nullable=False),
            sa.Column("challenge_title", sa.String(length=128), nullable=False),
            sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("difficulty_level", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("real_life_session_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
            sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("penalty_applied", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("badge_awarded", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["real_life_session_id"], ["real_life_sessions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = inspect(bind)
    if _table_exists(inspector, "daily_challenge_attempts"):
        for name, columns in [
            ("ix_daily_challenge_attempts_id", ["id"]),
            ("ix_daily_challenge_attempts_user_id", ["user_id"]),
            ("ix_daily_challenge_attempts_day_date", ["day_date"]),
            ("ix_daily_challenge_attempts_real_life_session_id", ["real_life_session_id"]),
        ]:
            if not _index_exists(inspector, "daily_challenge_attempts", name):
                op.create_index(name, "daily_challenge_attempts", columns)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "daily_challenge_attempts"):
        for idx in inspector.get_indexes("daily_challenge_attempts"):
            op.drop_index(idx["name"], table_name="daily_challenge_attempts")
        op.drop_table("daily_challenge_attempts")
