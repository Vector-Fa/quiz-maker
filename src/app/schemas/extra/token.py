from pydantic import BaseModel, PositiveInt


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str | None = None


class TokenData(BaseModel):
    user_id: PositiveInt
    is_admin: bool
    exp: int
