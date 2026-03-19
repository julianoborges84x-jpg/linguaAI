"""sessions xp and daily activity

Revision ID: 0003_sessions_xp_daily_activity
Revises: 0002_learna_modules
Create Date: 2026-02-27 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0003_sessions_xp_daily_activity"
down_revision = "0002_learna_modules"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    tables = set(inspector.get_table_names())

    if "xp_total" not in user_columns:
        op.add_column("users", sa.Column("xp_total", sa.Integer(), nullable=False, server_default="0"))

    op.alter_column("users", "timezone", existing_type=sa.String(length=64), server_default="America/Sao_Paulo")

    if "daily_activities" not in tables:
        op.create_table(
            "daily_activities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("day_date", sa.Date(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.UniqueConstraint("user_id", "day_date", name="uq_daily_activity_user_day"),
        )
        op.create_index("ix_daily_activities_id", "daily_activities", ["id"], unique=False)
        op.create_index("ix_daily_activities_user_id", "daily_activities", ["user_id"], unique=False)

    if "study_sessions" not in tables:
        op.create_table(
            "study_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("mode", sa.String(length=32), nullable=False),
            sa.Column("topic_id", sa.Integer(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("interactions_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
        )
        op.create_index("ix_study_sessions_id", "study_sessions", ["id"], unique=False)
        op.create_index("ix_study_sessions_user_id", "study_sessions", ["user_id"], unique=False)


def downgrade():
    op.drop_index("ix_study_sessions_user_id", table_name="study_sessions")
    op.drop_index("ix_study_sessions_id", table_name="study_sessions")
    op.drop_table("study_sessions")

    op.drop_index("ix_daily_activities_user_id", table_name="daily_activities")
    op.drop_index("ix_daily_activities_id", table_name="daily_activities")
    op.drop_table("daily_activities")

    op.alter_column("users", "timezone", existing_type=sa.String(length=64), server_default=None)
    op.drop_column("users", "xp_total")
