from typing import Dict, Optional
from sqlalchemy import insert, select
from app.database import async_session_maker
from sqlalchemy.exc import SQLAlchemyError

from app.utils.exception_handlers import handle_db_exception, handle_unexpected_exception


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[dict]:
        try:
            async with async_session_maker() as session:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            
        except (
            SQLAlchemyError, 
            Exception
        ) as e:
            extra = dict(**filter_by)

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)


    @classmethod
    async def find_all(cls, **filter_by) -> list[dict]:
        try:
            async with async_session_maker() as session:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().all()
        
        except (
            SQLAlchemyError, 
            Exception
        ) as e:
            extra = dict(**filter_by)

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)
        

    @classmethod
    async def add(cls, **data) -> None:
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**data).returning(cls.model)
                await session.execute(query)
                await session.commit()

        except (
            SQLAlchemyError, 
            Exception
        ) as e:
            extra = dict(**data)

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)
            