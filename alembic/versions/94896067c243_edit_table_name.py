"""edit table name

Revision ID: 94896067c243
Revises: 3100638639f5
Create Date: 2023-09-04 22:12:14.221438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94896067c243'
down_revision: Union[str, None] = '3100638639f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
