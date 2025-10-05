"""add user telegram fields

Revision ID: 8b6a9d2e7f0a
Revises: 83a4b57ca6c3
Create Date: 2025-10-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b6a9d2e7f0a'
down_revision: Union[str, Sequence[str], None] = '83a4b57ca6c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add Telegram-specific fields to users."""
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_bot', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('users', sa.Column('language_code', sa.String(length=16), nullable=True))
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), server_default=sa.false(), nullable=False))

    # Опционально убрать server_default после заполнения значений (оставляем как есть)


def downgrade() -> None:
    """Downgrade schema: drop added Telegram-specific fields from users."""
    op.drop_column('users', 'is_premium')
    op.drop_column('users', 'language_code')
    op.drop_column('users', 'is_bot')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'username')
