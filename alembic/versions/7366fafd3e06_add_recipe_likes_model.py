"""Add Recipe Likes model

Revision ID: 7366fafd3e06
Revises: 2dc5017ad955
Create Date: 2025-03-05 11:36:41.937652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7366fafd3e06'
down_revision: Union[str, None] = '2dc5017ad955'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('recipe_likes',
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('recipeId', sa.Integer(), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['recipeId'], ['recipes.id'], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint('userId', 'recipeId')
    )


def downgrade() -> None:
    op.drop_table('recipe_likes')

