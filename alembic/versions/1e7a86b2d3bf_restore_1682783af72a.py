"""restore 1682783af72a

Revision ID: 1e7a86b2d3bf
Revises: ec08a6c8e959
Create Date: 2025-10-05 16:27:25.670234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e7a86b2d3bf'
down_revision: Union[str, Sequence[str], None] = 'ec08a6c8e959'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
