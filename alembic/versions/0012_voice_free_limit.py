"""voice free limit

Revision ID: 0012_voice_free_limit
Revises: 0011_referral_pro_access
Create Date: 2026-03-18 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0012_voice_free_limit"
down_revision = "0011_referral_pro_access"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "users"):
        cols = _column_names(inspector, "users")
        if "voice_messages_used" not in cols:
            op.add_column("users", sa.Column("voice_messages_used", sa.Integer(), nullable=False, server_default="0"))
        if "voice_usage_reset_at" not in cols:
            op.add_column("users", sa.Column("voice_usage_reset_at", sa.Date(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "users"):
        cols = _column_names(inspector, "users")
        if "voice_usage_reset_at" in cols:
            op.drop_column("users", "voice_usage_reset_at")
        if "voice_messages_used" in cols:
            op.drop_column("users", "voice_messages_used")
