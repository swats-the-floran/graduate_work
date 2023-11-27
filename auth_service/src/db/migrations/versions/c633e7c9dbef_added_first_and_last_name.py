"""Added first and last name

Revision ID: c633e7c9dbef
Revises: edc6a3dc1382
Create Date: 2023-10-01 21:58:00.133859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c633e7c9dbef'
down_revision = 'edc6a3dc1382'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('first_name', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('second_name', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'second_name')
    op.drop_column('users', 'first_name')
    # ### end Alembic commands ###
