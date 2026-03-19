"""user onboarding completed flag

Revision ID: 0004_user_onboarding_completed
Revises: 0003_sessions_xp_daily_activity
Create Date: 2026-02-28 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0004_user_onboarding_completed"
down_revision = "0003_sessions_xp_daily_activity"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "onboarding_completed" not in user_columns:
        op.add_column(
            "users",
            sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade():
    op.drop_column("users", "onboarding_completed")
