"""merge heads after product images

Revision ID: 2caba12c368a
Revises: ab12cd34ef56, ec99b1c0abcd
Create Date: 2025-10-05 17:46:55.362916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2caba12c368a'
down_revision: Union[str, Sequence[str], None] = ('ab12cd34ef56', 'ec99b1c0abcd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
