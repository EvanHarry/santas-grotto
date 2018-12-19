"""Generate Stock model

Revision ID: 2884bbf99488
Revises: d01dcb8d06c0
Create Date: 2018-12-18 20:54:13.743209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2884bbf99488'
down_revision = 'd01dcb8d06c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supplier_code', sa.String(), nullable=True),
    sa.Column('tidings_code', sa.String(), nullable=True),
    sa.Column('supplier', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('last_modified', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stock')
    # ### end Alembic commands ###