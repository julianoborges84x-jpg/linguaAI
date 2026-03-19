"""users verification fields

Revision ID: 0006_users_verification_fields
Revises: 0005_users_target_language
Create Date: 2026-03-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0006_users_verification_fields"
down_revision = "0005_users_target_language"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}

    if "is_verified" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if "verification_token" not in user_columns:
        op.add_column("users", sa.Column("verification_token", sa.String(length=255), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}

    if "verification_token" in user_columns:
        op.drop_column("users", "verification_token")

    if "is_verified" in user_columns:
        op.drop_column("users", "is_verified")
