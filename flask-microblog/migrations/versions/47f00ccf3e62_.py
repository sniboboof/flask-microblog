"""empty message

Revision ID: 47f00ccf3e62
Revises: a0acff4f976
Create Date: 2014-04-12 03:47:42.881342

"""

# revision identifiers, used by Alembic.
revision = '47f00ccf3e62'
down_revision = 'a0acff4f976'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=63), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('categories',
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('blag_post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blag_post_id'], ['blag_post.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('categories')
    op.drop_table('category')
    ### end Alembic commands ###