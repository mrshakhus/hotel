from fastapi import Response
from app.exceptions import BookingAPIException, PasswordsDoNotMatchException, UserAlreadyExistsException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDAO
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception


class UsersService:
    @staticmethod
    async def register_user(
        email: str,
        password: str
    ) -> None:
        try:
            user_exists_already = await UsersDAO.find_one_or_none(email=email)
            if user_exists_already:
                raise UserAlreadyExistsException
            
            hashed_password = get_password_hash(password)
            await UsersDAO.add(email=email, hashed_password=hashed_password)

        except(
            UserAlreadyExistsException,
            BookingAPIException,
            Exception
        ) as e:
            extra = {
                "email": email
            }

            handle_exception(e, UserAlreadyExistsException, extra)
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)


    @staticmethod
    async def login_user(
        response: Response,
        email: str,
        password: str
    ) -> str:
        try:
            user = await authenticate_user(email, password)
            access_token = create_access_token({"sub": str(user["id"])})
            response.set_cookie("booking_access_token", access_token, httponly=True)

            return access_token
        
        except(
            BookingAPIException,
            Exception
        ) as e:
            extra = {
                "email": email
            }
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)
    

    @staticmethod
    async def change_password(
        old_password: str,
        new_password_1: str,
        new_password_2: str,
        email: str,
    ) -> str:
        try:
            await authenticate_user(email, old_password)
            if new_password_1 != new_password_2:
                raise PasswordsDoNotMatchException
            
            new_password = get_password_hash(new_password_1)
            await UsersDAO.change_password(email, new_password)
        
        except(
            BookingAPIException,
            Exception
        ) as e:
            extra = {
                "email": email
            }
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)