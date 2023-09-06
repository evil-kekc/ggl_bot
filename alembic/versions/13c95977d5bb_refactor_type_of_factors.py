"""refactor type of factors

Revision ID: 13c95977d5bb
Revises: 94896067c243
Create Date: 2023-09-06 20:40:11.253385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13c95977d5bb'
down_revision: Union[str, None] = '94896067c243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
