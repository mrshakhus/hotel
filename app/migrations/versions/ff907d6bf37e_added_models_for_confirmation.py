"""Added models for confirmation

Revision ID: ff907d6bf37e
Revises: f6ec42060ea6
Create Date: 2024-08-05 16:19:17.981021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff907d6bf37e'
down_revision: Union[str, None] = 'f6ec42060ea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booking_confirmations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('is_confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('booking_confirmations')
    # ### end Alembic commands ###
