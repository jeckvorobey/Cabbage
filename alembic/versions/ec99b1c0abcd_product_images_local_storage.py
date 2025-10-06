"""product images local storage

Revision ID: ec99b1c0abcd
Revises: 56875899c288
Create Date: 2025-10-05 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec99b1c0abcd'
down_revision: Union[str, Sequence[str], None] = '56875899c288'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create product_images, migrate and drop products.image_url."""
    op.create_table(
        'product_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_images_product_id'), 'product_images', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_images_is_primary'), 'product_images', ['is_primary'], unique=False)

    # Частичный уникальный индекс: только одно главное изображение на товар
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_product_images_primary_per_product
        ON product_images(product_id)
        WHERE is_primary = true;
        """
    )

    # Перенос данных из products.image_url (если колонка существует)
    conn = op.get_bind()
    try:
        rows = conn.execute(sa.text("SELECT id, image_url FROM products WHERE image_url IS NOT NULL")).fetchall()
        for pid, url in rows:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO product_images (product_id, file_path, is_primary, sort_order, created_at)
                    VALUES (:pid, :url, true, 0, NOW())
                    """
                ),
                {"pid": pid, "url": url}
            )
    except Exception:
        # Колонка могла быть уже удалена в предыдущих ревизиях — игнорируем
        pass

    # Удалить колонку image_url, если она есть
    with op.batch_alter_table('products') as batch_op:
        try:
            batch_op.drop_column('image_url')
        except Exception:
            pass


def downgrade() -> None:
    """Downgrade schema: recreate products.image_url and drop product_images."""
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=500), nullable=True))

    op.execute("DROP INDEX IF EXISTS uq_product_images_primary_per_product")
    op.drop_index(op.f('ix_product_images_is_primary'), table_name='product_images')
    op.drop_index(op.f('ix_product_images_product_id'), table_name='product_images')
    op.drop_table('product_images')
