from datetime import datetime, timezone
from sqlalchemy import select
from app.dao.base import BaseDAO
from app.users.models import Users
from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_maker
from app.utils.exception_handlers import handle_db_exception, handle_exception, handle_unexpected_exception


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def change_password(
        cls,
        email: str,
        new_password: str
    ) -> None:
        try:
            async with async_session_maker() as session:
                get_user = (
                    select(Users)
                    .where(Users.email == email)
                )

                result = await session.execute(get_user)
                user = result.scalars().first()
                user.hashed_password = new_password
                user.password_changed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()

        except (
            SQLAlchemyError, 
            Exception,
        ) as e:

            extra = { 
                "email": email
            }
            
            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)
