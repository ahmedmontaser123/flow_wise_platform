"""add ATS scores to applications

Revision ID: c2d4e8b7a901
Revises: aa7da30d5100
"""

from alembic import op
import sqlalchemy as sa


revision = "c2d4e8b7a901"
down_revision = "aa7da30d5100"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("ats_score", sa.Float(), nullable=True))
    op.add_column("applications", sa.Column("score_breakdown", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("applications", "score_breakdown")
    op.drop_column("applications", "ats_score")
