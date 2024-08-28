from fastapi import APIRouter, Depends, Response

from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SChangingPassword, SToken, SUserAuth, SUserInfo
from app.users.service import UsersService


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и регистрация"]
)

@router.post("/register", status_code=201)
async def register_user(user_data: SUserAuth):
    await UsersService.register_user(user_data.email, user_data.password)
    return {"meassage": "Вы успешно зарегистрировались."}


@router.post("/login", status_code=200, response_model=SToken)
async def login_user(
    response: Response, 
    user_data: SUserAuth
):
    access_token = await UsersService.login_user(
        response, 
        user_data.email, 
        user_data.password
    )
    return {"token": access_token}


@router.post("/password", status_code=200)
async def change_password(
    passwords: SChangingPassword,
    user: Users = Depends(get_current_user)
):
    await UsersService.change_password(
        passwords.old_password,
        passwords.new_password_1,
        passwords.new_password_2,
        user["email"],
    )
    return {"message": "Пороль успешно изменен."}


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

    
    