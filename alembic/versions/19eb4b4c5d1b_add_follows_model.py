"""Add Follows model

Revision ID: 19eb4b4c5d1b
Revises: cccf9b0ed470
Create Date: 2025-03-05 11:12:41.830238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19eb4b4c5d1b'
down_revision: Union[str, None] = 'cccf9b0ed470'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('follows',
    sa.Column('followerId', sa.Integer(), nullable=False),
    sa.Column('followeeId', sa.Integer(), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['followeeId'], ['users.id'], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['followerId'], ['users.id'], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint('followerId', 'followeeId')
    )


def downgrade() -> None:
    op.drop_table('follows')
