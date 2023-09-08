"""add total results columns

Revision ID: e7cc7097db61
Revises: c3282b538801
Create Date: 2023-09-08 12:03:01.244391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7cc7097db61'
down_revision: Union[str, None] = 'c3282b538801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
