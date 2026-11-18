"""merge dashboard and HR migration heads

Revision ID: d4e8f6a1b203
Revises: c2d4e8b7a901, c3f1a9e7b2d4
"""

from typing import Sequence, Union


revision: str = "d4e8f6a1b203"
down_revision: Union[str, Sequence[str], None] = (
    "c2d4e8b7a901",
    "c3f1a9e7b2d4",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge the two already-applied migration branches."""


def downgrade() -> None:
    """Restore the two migration heads without changing database objects."""
