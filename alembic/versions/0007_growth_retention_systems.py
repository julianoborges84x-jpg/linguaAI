"""growth retention systems

Revision ID: 0007_growth_retention_systems
Revises: 0006_users_verification_fields
Create Date: 2026-03-16 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0007_growth_retention_systems"
down_revision = "0006_users_verification_fields"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "users"):
        user_columns = _column_names(inspector, "users")

        if "current_streak" not in user_columns:
            op.add_column("users", sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"))
        if "longest_streak" not in user_columns:
            op.add_column("users", sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"))
        if "last_active_date" not in user_columns:
            op.add_column("users", sa.Column("last_active_date", sa.Date(), nullable=True))
        if "referral_code" not in user_columns:
            op.add_column("users", sa.Column("referral_code", sa.String(length=32), nullable=True))
        if "referred_by_user_id" not in user_columns:
            op.add_column("users", sa.Column("referred_by_user_id", sa.Integer(), nullable=True))
        if "referred_count" not in user_columns:
            op.add_column("users", sa.Column("referred_count", sa.Integer(), nullable=False, server_default="0"))

        inspector = inspect(bind)
        if not _index_exists(inspector, "users", "ix_users_referral_code"):
            op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)

        fks = {fk["name"] for fk in inspector.get_foreign_keys("users") if fk.get("name")}
        if "fk_users_referred_by_user_id_users" not in fks:
            op.create_foreign_key(
                "fk_users_referred_by_user_id_users",
                "users",
                "users",
                ["referred_by_user_id"],
                ["id"],
            )

    inspector = inspect(bind)
    if not _table_exists(inspector, "daily_mission_progress"):
        op.create_table(
            "daily_mission_progress",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("day_date", sa.Date(), nullable=False),
            sa.Column("target_sessions", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("completed_sessions", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("bonus_xp_awarded", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "day_date", name="uq_daily_mission_user_day"),
        )
        op.create_index("ix_daily_mission_progress_id", "daily_mission_progress", ["id"])
        op.create_index("ix_daily_mission_progress_user_id", "daily_mission_progress", ["user_id"])

    inspector = inspect(bind)
    if not _table_exists(inspector, "analytics_events"):
        op.create_table(
            "analytics_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_analytics_events_id", "analytics_events", ["id"])
        op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
        op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
        op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "analytics_events"):
        for idx in inspector.get_indexes("analytics_events"):
            op.drop_index(idx["name"], table_name="analytics_events")
        op.drop_table("analytics_events")

    inspector = inspect(bind)
    if _table_exists(inspector, "daily_mission_progress"):
        for idx in inspector.get_indexes("daily_mission_progress"):
            op.drop_index(idx["name"], table_name="daily_mission_progress")
        op.drop_table("daily_mission_progress")

    inspector = inspect(bind)
    if _table_exists(inspector, "users"):
        user_columns = _column_names(inspector, "users")
        fks = {fk["name"] for fk in inspector.get_foreign_keys("users") if fk.get("name")}
        if "fk_users_referred_by_user_id_users" in fks:
            op.drop_constraint("fk_users_referred_by_user_id_users", "users", type_="foreignkey")
        if _index_exists(inspector, "users", "ix_users_referral_code"):
            op.drop_index("ix_users_referral_code", table_name="users")
        if "referred_count" in user_columns:
            op.drop_column("users", "referred_count")
        if "referred_by_user_id" in user_columns:
            op.drop_column("users", "referred_by_user_id")
        if "referral_code" in user_columns:
            op.drop_column("users", "referral_code")
        if "last_active_date" in user_columns:
            op.drop_column("users", "last_active_date")
        if "longest_streak" in user_columns:
            op.drop_column("users", "longest_streak")
        if "current_streak" in user_columns:
            op.drop_column("users", "current_streak")
