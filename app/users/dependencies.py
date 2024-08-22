from datetime import datetime, timezone
from fastapi import Depends, Request
from jose import JWTError, jwt
from app.config import settings
from app.exceptions import IncorrectTokenFortmatException, NoRightsException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException
from app.users.dao import UsersDAO
from app.users.enums import UserRole
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        print("ERROR")
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFortmatException
    
    expire: str = payload.get("exp")
    if not expire or int(expire) < datetime.now(timezone.utc).timestamp():
        raise TokenExpiredException
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    
    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    
    user_info = dict()
    user_info["id"] = user["id"]
    user_info["email"] = user["email"]
    
    return user_info


async def check_role(
    required_roles: list[UserRole], 
    user: Users = Depends(get_current_user)
):
    if user.role not in required_roles:
        raise NoRightsException
    return user