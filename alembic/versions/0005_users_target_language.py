"""users target_language column

Revision ID: 0005_users_target_language
Revises: 0004_user_onboarding_completed
Create Date: 2026-02-28 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0005_users_target_language"
down_revision = "0004_user_onboarding_completed"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("target_language", sa.String(length=8), nullable=True))


def downgrade():
    op.drop_column("users", "target_language")
