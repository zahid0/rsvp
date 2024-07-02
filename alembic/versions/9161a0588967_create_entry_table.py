"""create entry table

Revision ID: 9161a0588967
Revises: 
Create Date: 2024-07-02 09:09:14.228006

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9161a0588967"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entries_id"), "entries", ["id"], unique=False)
    op.create_index(op.f("ix_entries_path"), "entries", ["path"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_entries_path"), table_name="entries")
    op.drop_index(op.f("ix_entries_id"), table_name="entries")
    op.drop_table("entries")
    # ### end Alembic commands ###
