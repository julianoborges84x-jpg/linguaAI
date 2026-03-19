"""referral pro access

Revision ID: 0011_referral_pro_access
Revises: 0010_daily_challenge_mode
Create Date: 2026-03-17 00:30:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0011_referral_pro_access"
down_revision = "0010_daily_challenge_mode"
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
        if "pro_access_until" not in cols:
            op.add_column("users", sa.Column("pro_access_until", sa.Date(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "users"):
        cols = _column_names(inspector, "users")
        if "pro_access_until" in cols:
            op.drop_column("users", "pro_access_until")
