"""added new table FavoriteHotels

Revision ID: 1225fa4849e2
Revises: d424fe885169
Create Date: 2024-08-21 00:11:26.117121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1225fa4849e2'
down_revision: Union[str, None] = 'd424fe885169'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_location_tsv', table_name='hotels', postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_location_tsv', 'hotels', ['tsvector'], unique=False, postgresql_using='gin')
    # ### end Alembic commands ###