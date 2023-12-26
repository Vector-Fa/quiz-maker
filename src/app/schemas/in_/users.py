from typing import Annotated

from pydantic import BaseModel, EmailStr, PositiveInt, StringConstraints

from src.app.schemas.types import StrongPassword


class EmailRegisterIn(BaseModel):
    email: EmailStr


# ====-----====
class UserRegisterIn(BaseModel):
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=4, max_length=50)]
    password: StrongPassword
    verify_code: PositiveInt


# ====-----====
class UserLoginIn(BaseModel):
    email: EmailStr
    password: str


# ====-----====
class RefreshTokenIn(BaseModel):
    refresh_token: str
