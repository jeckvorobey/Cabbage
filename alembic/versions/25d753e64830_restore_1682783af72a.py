"""restore 1682783af72a

Revision ID: 25d753e64830
Revises: 1e7a86b2d3bf
Create Date: 2025-10-05 16:30:41.540674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25d753e64830'
down_revision: Union[str, Sequence[str], None] = '1e7a86b2d3bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
