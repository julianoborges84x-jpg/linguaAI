"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "languages",
        sa.Column("iso_code", sa.String(length=8), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("region", sa.String(length=200), nullable=False),
        sa.Column("family", sa.String(length=200), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.Enum("FREE", "PRO", name="planenum"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("subscription_status", sa.String(length=50), nullable=True),
        sa.Column("target_language_code", sa.String(length=8), nullable=True),
        sa.Column("base_language_code", sa.String(length=8), nullable=True),
        sa.ForeignKeyConstraint(["target_language_code"], ["languages.iso_code"]),
        sa.ForeignKeyConstraint(["base_language_code"], ["languages.iso_code"]),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "learning_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("feature", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_learning_history_id", "learning_history", ["id"], unique=False)
    op.create_index("ix_learning_history_user_id", "learning_history", ["user_id"], unique=False)

    op.create_table(
        "daily_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("passage_id", sa.String(length=64), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id", "day", name="uq_daily_messages_user_day"),
    )
    op.create_index("ix_daily_messages_id", "daily_messages", ["id"], unique=False)
    op.create_index("ix_daily_messages_user_id", "daily_messages", ["user_id"], unique=False)

    op.create_table(
        "motivational_quotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
    )
    op.create_index("ix_motivational_quotes_id", "motivational_quotes", ["id"], unique=False)

    op.create_table(
        "motivational_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quote_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["quote_id"], ["motivational_quotes.id"]),
    )
    op.create_index("ix_motivational_events_id", "motivational_events", ["id"], unique=False)
    op.create_index("ix_motivational_events_user_id", "motivational_events", ["user_id"], unique=False)
    op.create_index("ix_motivational_events_quote_id", "motivational_events", ["quote_id"], unique=False)


def downgrade():
    op.drop_index("ix_motivational_events_quote_id", table_name="motivational_events")
    op.drop_index("ix_motivational_events_user_id", table_name="motivational_events")
    op.drop_index("ix_motivational_events_id", table_name="motivational_events")
    op.drop_table("motivational_events")

    op.drop_index("ix_motivational_quotes_id", table_name="motivational_quotes")
    op.drop_table("motivational_quotes")

    op.drop_index("ix_daily_messages_user_id", table_name="daily_messages")
    op.drop_index("ix_daily_messages_id", table_name="daily_messages")
    op.drop_table("daily_messages")

    op.drop_index("ix_learning_history_user_id", table_name="learning_history")
    op.drop_index("ix_learning_history_id", table_name="learning_history")
    op.drop_table("learning_history")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table("languages")

    op.execute("DROP TYPE IF EXISTS planenum")
