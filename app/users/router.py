from fastapi import APIRouter, Depends, Request, Response
from fastapi_versioning import version

from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SChangingPassword, SToken, SUserAuth, SUserInfo
from app.users.service import UsersService
from app.limiter import limiter


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и регистрация"]
)

@router.post("/register", status_code=201)
@version(1)
@limiter.limit("1/second")
async def register_user(
    request: Request,
    user_data: SUserAuth
):
    await UsersService.register_user(user_data.email, user_data.password)
    return {"meassage": "Вы успешно зарегистрировались."}


@router.post("/login", status_code=200, response_model=SToken)
@version(1)
@limiter.limit("1/second")
async def login_user(
    request: Request,
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
@version(1)
@limiter.limit("1/second")
async def change_password(
    request: Request,
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
@version(1)
@limiter.limit("1/second")
async def logout_user(
    request: Request,
    response: Response
):
    response.delete_cookie("booking_access_token")


@router.get("/me", status_code=200, response_model=SUserInfo)
@version(1)
@limiter.limit("1/second")
async def get_user_me(
    request: Request,
    current_user: Users = Depends(get_current_user)
):
    return current_user

    
    