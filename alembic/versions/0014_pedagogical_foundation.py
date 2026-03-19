"""pedagogical architecture foundation

Revision ID: 0014_pedagogical_foundation
Revises: 0013_oauth_social_fields
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0014_pedagogical_foundation"
down_revision = "0013_oauth_social_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "proficiency_levels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_proficiency_levels_code", "proficiency_levels", ["code"], unique=True)

    op.create_table(
        "learning_tracks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("cefr_level", sa.String(length=8), nullable=False),
    )
    op.create_index("ix_learning_tracks_slug", "learning_tracks", ["slug"], unique=True)

    op.create_table(
        "learning_modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("track_id", sa.Integer(), sa.ForeignKey("learning_tracks.id"), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("competency", sa.String(length=48), nullable=False),
    )
    op.create_index("ix_learning_modules_slug", "learning_modules", ["slug"], unique=True)

    op.create_table(
        "learning_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("learning_modules.id"), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("cefr_level", sa.String(length=8), nullable=False),
        sa.Column("learning_objective", sa.Text(), nullable=False, server_default=""),
        sa.Column("primary_skill", sa.String(length=64), nullable=False),
        sa.Column("secondary_skill", sa.String(length=64), nullable=True),
        sa.Column("prerequisites_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default="scenario"),
        sa.Column("is_pro_only", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "learning_objectives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("learning_units.id"), nullable=False),
        sa.Column("objective_text", sa.Text(), nullable=False),
    )

    op.create_table(
        "skill_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
    )
    op.create_index("ix_skill_tags_slug", "skill_tags", ["slug"], unique=True)

    op.create_table(
        "learner_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("estimated_level", sa.String(length=8), nullable=False, server_default="A1"),
        sa.Column("level_confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("speaking_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("listening_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vocabulary_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("grammar_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fluency_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_learner_profiles_user_id", "learner_profiles", ["user_id"], unique=True)

    op.create_table(
        "learner_weaknesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("skill_tag", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("occurrences", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "learner_strengths",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("skill_tag", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "grammar_mastery",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic", sa.String(length=96), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="learning"),
        sa.Column("last_practiced_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "vocabulary_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("term", sa.String(length=120), nullable=False),
        sa.Column("translation", sa.String(length=120), nullable=False),
        sa.Column("context", sa.String(length=180), nullable=False, server_default="general"),
        sa.Column("level", sa.String(length=8), nullable=False, server_default="A1"),
        sa.Column("category", sa.String(length=80), nullable=False, server_default="general"),
        sa.Column("example", sa.Text(), nullable=False, server_default=""),
        sa.Column("synonyms_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_table(
        "vocabulary_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("vocabulary_items.id"), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="new"),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_review_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "mistake_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("user_text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("context_feature", sa.String(length=64), nullable=False, server_default="chat"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "review_queue",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("queue_type", sa.String(length=48), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("due_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    for table in [
        "review_queue",
        "mistake_logs",
        "vocabulary_progress",
        "vocabulary_items",
        "grammar_mastery",
        "learner_strengths",
        "learner_weaknesses",
        "learner_profiles",
        "skill_tags",
        "learning_objectives",
        "learning_units",
        "learning_modules",
        "learning_tracks",
        "proficiency_levels",
    ]:
        op.drop_table(table)
