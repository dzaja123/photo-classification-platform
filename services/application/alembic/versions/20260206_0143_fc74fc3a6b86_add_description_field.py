"""add_description_field

Revision ID: fc74fc3a6b86
Revises: 5295ca020b50
Create Date: 2026-02-06 01:43:10.796322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fc74fc3a6b86"
down_revision: Union[str, None] = "5295ca020b50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("submissions", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("submissions", "description")
