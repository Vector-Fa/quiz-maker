from fastapi import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import User
from src.app.repositories import UserRepository
from src.app.schemas.extra.token import TokenData
from src.core.excpetions.http_exceptions import (
    UnAuthorizedException,
    BadRequestException,
)
from src.core.excpetions.jwt_exceptions import (
    JwtTokenExpiredException,
    BadJwtTokenException,
)
from src.core.security import JWTHandler


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login-form", auto_error=False)
http_bearer = HTTPBearer()


def check_bearer(scheme: str) -> None:
    if scheme != "Bearer":
        raise BadRequestException("bad token", "bad_token")


def decode_token(token_credentials: str) -> dict:
    try:
        token = JWTHandler.decode_access(token_credentials)
        return token
    except JwtTokenExpiredException:
        raise UnAuthorizedException("login again", "login_again")
    except BadJwtTokenException:
        raise BadRequestException("could not verify jwt token", "bad_token")


def authentication_required(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> TokenData:
    check_bearer(scheme=credentials.scheme)
    token = decode_token(token_credentials=credentials.credentials)
    user_id = token.get("user_id")
    if not user_id:
        raise BadRequestException("bad token", "bad_token")

    return TokenData(
        user_id=user_id, exp=token.get("exp"), is_admin=token.get("is_admin")
    )


async def get_current_user(db_session: AsyncSession, user_id: int) -> User:
    user_repository = UserRepository(db_session)
    user = await user_repository.get_by_id(user_id)
    return user
