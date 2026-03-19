"""learna modules tables

Revision ID: 0002_learna_modules
Revises: 0001_initial
Create Date: 2026-02-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0002_learna_modules"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "topics" not in tables:
        op.create_table(
            "topics",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False),
        )
        op.create_index("ix_topics_id", "topics", ["id"], unique=False)
        op.create_index("ix_topics_name", "topics", ["name"], unique=True)

    if "messages" not in tables:
        op.create_table(
            "messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("corrected", sa.Text(), nullable=False),
            sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        )
        op.create_index("ix_messages_id", "messages", ["id"], unique=False)
        op.create_index("ix_messages_user_id", "messages", ["user_id"], unique=False)

    if "vocabulary" not in tables:
        op.create_table(
            "vocabulary",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("word", sa.String(length=80), nullable=False),
            sa.Column("definition", sa.Text(), nullable=False),
            sa.Column("example", sa.Text(), nullable=False),
        )
        op.create_index("ix_vocabulary_id", "vocabulary", ["id"], unique=False)
        op.create_index("ix_vocabulary_word", "vocabulary", ["word"], unique=True)

    if "progress" not in tables:
        op.create_table(
            "progress",
            sa.Column("user_id", sa.Integer(), primary_key=True),
            sa.Column("streak", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("hours_spoken", sa.Float(), nullable=False, server_default="0"),
            sa.Column("words_learned", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        )


def downgrade():
    op.drop_table("progress")

    op.drop_index("ix_vocabulary_word", table_name="vocabulary")
    op.drop_index("ix_vocabulary_id", table_name="vocabulary")
    op.drop_table("vocabulary")

    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_index("ix_messages_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_topics_name", table_name="topics")
    op.drop_index("ix_topics_id", table_name="topics")
    op.drop_table("topics")
