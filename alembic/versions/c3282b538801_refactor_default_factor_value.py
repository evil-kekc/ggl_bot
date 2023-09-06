"""refactor default factor value

Revision ID: c3282b538801
Revises: 13c95977d5bb
Create Date: 2023-09-06 21:11:51.408796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3282b538801'
down_revision: Union[str, None] = '13c95977d5bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
