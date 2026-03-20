"""multilingual curriculum and click-learning progress

Revision ID: 0015_multilang_click_learning
Revises: 0014_pedagogical_foundation
Create Date: 2026-03-19
"""

from alembic import op
import sqlalchemy as sa


revision = "0015_multilang_click_learning"
down_revision = "0014_pedagogical_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learning_tracks",
        sa.Column("target_language_code", sa.String(length=8), nullable=False, server_default="en"),
    )
    op.create_index("ix_learning_tracks_target_language_code", "learning_tracks", ["target_language_code"], unique=False)

    op.add_column(
        "vocabulary_items",
        sa.Column("language_code", sa.String(length=8), nullable=False, server_default="en"),
    )
    op.create_index("ix_vocabulary_items_language_code", "vocabulary_items", ["language_code"], unique=False)

    op.create_table(
        "learning_unit_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("learning_units.id"), nullable=False),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_steps", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_learning_unit_progress_user_id", "learning_unit_progress", ["user_id"], unique=False)
    op.create_index("ix_learning_unit_progress_unit_id", "learning_unit_progress", ["unit_id"], unique=False)
    op.create_index(
        "ux_learning_unit_progress_user_unit",
        "learning_unit_progress",
        ["user_id", "unit_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_learning_unit_progress_user_unit", table_name="learning_unit_progress")
    op.drop_index("ix_learning_unit_progress_unit_id", table_name="learning_unit_progress")
    op.drop_index("ix_learning_unit_progress_user_id", table_name="learning_unit_progress")
    op.drop_table("learning_unit_progress")

    op.drop_index("ix_vocabulary_items_language_code", table_name="vocabulary_items")
    op.drop_column("vocabulary_items", "language_code")

    op.drop_index("ix_learning_tracks_target_language_code", table_name="learning_tracks")
    op.drop_column("learning_tracks", "target_language_code")
