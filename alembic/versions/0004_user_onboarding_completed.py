"""user onboarding completed flag

Revision ID: 0004_user_onboarding_completed
Revises: 0003_sessions_xp_daily_activity
Create Date: 2026-02-28 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0004_user_onboarding_completed"
down_revision = "0003_sessions_xp_daily_activity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column("users", "onboarding_completed")
