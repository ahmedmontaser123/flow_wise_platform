"""add CV file hash column

Revision ID: e5f7a9b2c314
Revises: d4e8f6a1b203
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e5f7a9b2c314"
down_revision: Union[str, None] = "d4e8f6a1b203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cv_files",
        sa.Column("file_hash", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cv_files", "file_hash")
