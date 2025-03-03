"""create forkedCount in recipes table

Revision ID: 1e65acd53b9a
Revises: 
Create Date: 2025-03-03 11:42:11.908248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e65acd53b9a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('recipes', sa.Column('forkedCount', sa.Integer(), default=0))


def downgrade() -> None:
    op.drop_column('recipes','forkedCount')
