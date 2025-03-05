"""Add Cooking History model

Revision ID: bd23f2591dc9
Revises: 7366fafd3e06
Create Date: 2025-03-05 11:39:23.623012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd23f2591dc9'
down_revision: Union[str, None] = '7366fafd3e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cooking_historys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('recipeId', sa.Integer(), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('updatedAt', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
    sa.ForeignKeyConstraint(['recipeId'], ['recipes.id'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cooking_historys_id'), 'cooking_historys', ['id'], unique=False)
    

def downgrade() -> None:
    op.drop_index(op.f('ix_cooking_historys_id'), table_name='cooking_historys')
    op.drop_table('cooking_historys')
