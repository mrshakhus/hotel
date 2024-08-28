import enum
from pydantic import BaseModel, EmailStr, Field


class SUserAuth(BaseModel):
    email: EmailStr
    password: str


class SUserInfo(BaseModel):
    id: int = Field(..., gt=0)
    email: EmailStr


class SToken(BaseModel):
    token: str

class SChangingPassword(BaseModel):
    old_password: str
    new_password_1: str
    new_password_2: str
