"""total words column in progress

Revision ID: 83a73ccd689f
Revises: af75e7b5a8b6
Create Date: 2024-08-06 09:05:03.275407

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "83a73ccd689f"
down_revision: Union[str, None] = "af75e7b5a8b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "reading_progresses", sa.Column("total_words", sa.Integer(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("reading_progresses", "total_words")
    # ### end Alembic commands ###
