"""add bug report table

Revision ID: d63be4a8086d
Revises: e7cc7097db61
Create Date: 2023-09-16 13:13:23.438927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd63be4a8086d'
down_revision: Union[str, None] = 'e7cc7097db61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
