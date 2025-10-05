"""add carts and cart_items tables

Revision ID: ab12cd34ef56
Revises: 56875899c288
Create Date: 2025-10-05 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab12cd34ef56'
# ВАЖНО: укажите корректный down_revision — последний revision в вашем дереве миграций
# Здесь установлен на 56875899c288 (последняя пустая миграция), при необходимости скорректируйте.
down_revision: Union[str, Sequence[str], None] = '56875899c288'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_carts_user_id'), 'carts', ['user_id'], unique=True)

    op.create_table(
        'cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cart_items_cart_id'), 'cart_items', ['cart_id'], unique=False)
    op.create_unique_constraint('uq_cart_product', 'cart_items', ['cart_id', 'product_id'])


def downgrade() -> None:
    op.drop_constraint('uq_cart_product', 'cart_items', type_='unique')
    op.drop_index(op.f('ix_cart_items_cart_id'), table_name='cart_items')
    op.drop_table('cart_items')
    op.drop_index(op.f('ix_carts_user_id'), table_name='carts')
    op.drop_table('carts')
