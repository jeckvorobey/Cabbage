"""merge heads

Revision ID: d56bc6277e3a
Revises: 8b6a9d2e7f0a, dd5f84b0d2d0
Create Date: 2025-10-05 14:28:47.900400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd56bc6277e3a'
down_revision: Union[str, Sequence[str], None] = ('8b6a9d2e7f0a', 'dd5f84b0d2d0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
