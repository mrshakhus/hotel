from fastapi import APIRouter, Depends, Response

from app.exceptions import UserAlreadyExistsException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SToken, SUserAuth, SUserInfo


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и регистрация"]
)

@router.post("/register", status_code=201)
async def register_user(user_data: SUserAuth):
    user_exists_already = await UsersDAO.find_one_or_none(email=user_data.email)
    if user_exists_already:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password)


@router.post("/login", status_code=200, response_model=SToken)
async def login_user(
    response: Response, 
    user_data: SUserAuth
):
    user = await authenticate_user(user_data.email, user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"token": access_token}


@router.post("/logout", status_code=204)
async def logout_user(
    response: Response
):
    response.delete_cookie("booking_access_token")


@router.get("/me", status_code=200, response_model=SUserInfo)
async def get_user_me(
    current_user: Users = Depends(get_current_user)
):
    return current_user

    
    