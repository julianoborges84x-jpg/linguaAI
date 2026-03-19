"""users target_language column

Revision ID: 0005_users_target_language
Revises: 0004_user_onboarding_completed
Create Date: 2026-02-28 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0005_users_target_language"
down_revision = "0004_user_onboarding_completed"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "target_language" not in user_columns:
        op.add_column("users", sa.Column("target_language", sa.String(length=8), nullable=True))


def downgrade():
    op.drop_column("users", "target_language")
