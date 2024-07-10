"""reading config

Revision ID: 01cdbf12b631
Revises: 69c7e8ed29ca
Create Date: 2024-07-04 05:10:28.474660

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "01cdbf12b631"
down_revision: Union[str, None] = "69c7e8ed29ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reading_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("words_per_minute", sa.Integer(), nullable=True),
        sa.Column("number_of_words", sa.Integer(), nullable=True),
        sa.Column("font_size", sa.Integer(), nullable=True),
        sa.Column("sprint_minutes", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reading_configs_id"), "reading_configs", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_reading_configs_id"), table_name="reading_configs")
    op.drop_table("reading_configs")
    # ### end Alembic commands ###