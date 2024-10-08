"""added new column tsvector to Hotels and indexed it

Revision ID: d424fe885169
Revises: db03a326bc2f
Create Date: 2024-08-20 02:28:12.220907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd424fe885169'
down_revision: Union[str, None] = 'db03a326bc2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hotels', sa.Column('tsvector', postgresql.TSVECTOR()))
    # ### end Alembic commands ###

    # Шаг 2: Обновляем tsvector_column для всех существующих записей
    # Определяем таблицу и колонку для выполнения обновления
    hotels = table('hotels', column('location', sa.Text), column('tsvector', postgresql.TSVECTOR))
    
    # Обновляем tsvector для всех отелей
    op.execute(
        hotels.update()
        .values(tsvector=sa.func.to_tsvector('russian', hotels.c.location))
    )

    # Шаг 3: Делаем tsvector столбец NOT NULL
    op.alter_column('hotels', 'tsvector', nullable=False)

    # Шаг 4: Создаем индекс для оптимизации полнотекстового поиска
    op.create_index('idx_location_tsv', 'hotels', ['tsvector'], postgresql_using='gin')


def downgrade() -> None:
    # Шаг 1: Удаляем индекс
    op.drop_index('idx_location_tsv', table_name='hotels')

    # Шаг 2: Удаляем столбец
    op.drop_column('hotels', 'tsvector')
