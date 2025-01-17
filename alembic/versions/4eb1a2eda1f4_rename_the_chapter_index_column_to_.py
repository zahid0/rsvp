"""rename the chapter_index column to chapter id

Revision ID: 4eb1a2eda1f4
Revises: 745e028c5ef9
Create Date: 2024-07-10 03:10:48.244417

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4eb1a2eda1f4"
down_revision: Union[str, None] = "745e028c5ef9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "reading_progresses", sa.Column("chapter_id", sa.Integer(), nullable=True)
    )
    op.drop_column("reading_progresses", "chapter_index")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "reading_progresses",
        sa.Column("chapter_index", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("reading_progresses", "chapter_id")
    # ### end Alembic commands ###
