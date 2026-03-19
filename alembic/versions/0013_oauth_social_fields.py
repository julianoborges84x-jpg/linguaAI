"""add oauth provider columns on users

Revision ID: 0013_oauth_social_fields
Revises: 0012_voice_free_limit
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0013_oauth_social_fields"
down_revision = "0012_voice_free_limit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_sub", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("apple_sub", sa.String(length=255), nullable=True))
    op.create_index("ix_users_google_sub", "users", ["google_sub"], unique=True)
    op.create_index("ix_users_apple_sub", "users", ["apple_sub"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_apple_sub", table_name="users")
    op.drop_index("ix_users_google_sub", table_name="users")
    op.drop_column("users", "apple_sub")
    op.drop_column("users", "google_sub")
