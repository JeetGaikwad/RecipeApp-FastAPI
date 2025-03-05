"""Add Recipe Comments model

Revision ID: 2dc5017ad955
Revises: 6a727bdc568a
Create Date: 2025-03-05 11:32:39.446206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2dc5017ad955'
down_revision: Union[str, None] = '6a727bdc568a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('recipe_comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.Column('recipeId', sa.Integer(), nullable=False),
    sa.Column('parentCommentId', sa.Integer(), nullable=True),
    sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.Column('updatedAt', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
    sa.ForeignKeyConstraint(['parentCommentId'], ['recipe_comments.id'], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['recipeId'], ['recipes.id'], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_comments_id'), 'recipe_comments', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recipe_comments_id'), table_name='recipe_comments')
    op.drop_table('recipe_comments')
