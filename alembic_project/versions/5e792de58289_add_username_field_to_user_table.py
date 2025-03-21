"""Add username field to User table

Revision ID: 5e792de58289
Revises: 1f3a690654fc
Create Date: 2025-03-21 13:13:24.697140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e792de58289'
down_revision = '1f3a690654fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')
    # ### end Alembic commands ### 