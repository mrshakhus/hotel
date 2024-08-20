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
