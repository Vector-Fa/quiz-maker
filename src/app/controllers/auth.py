import random

from fastapi import BackgroundTasks

from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.extra.token import TokenOut
from src.app.schemas.out.users import UserOut
from src.core.excpetions import BadRequestException, UnAuthorizedException
from src.core.security import JWTHandler, PasswordHandler
from ...core.cache.redis_client import RedisClient

from ...core.excpetions.http_exceptions import UnProcessableEntityException
from ..repositories.user import UserRepository
from src.core.auth.email_client import EmailClient
from ...core.excpetions.jwt_exceptions import (
    JwtTokenExpiredException,
    BadJwtTokenException,
)


class AuthController:
    password_handler = PasswordHandler
    jwt_handler = JWTHandler

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def send_verify_code(
        self,
        user_email: str,
        background_tasks: BackgroundTasks,
        email_client: EmailClient,
        redis_client: RedisClient,
    ) -> MessageResponse:
        if await self.user_repository.email_exists(user_email):
            raise BadRequestException("Email already exists", "email_exists")
        if await redis_client.get(user_email):
            raise BadRequestException("wait two minute for resend", "spam_verify_code")

        verify_code = random.randint(11111, 99999)
        background_tasks.add_task(
            email_client.send, to_email=user_email, verify_code=verify_code
        )

        await redis_client.set(user_email, verify_code, 120)
        return MessageResponse(message="Code is sent")

    async def register_user(
        self,
        email: str,
        password: str,
        verify_code_in: int,
        full_name: str,
        redis_client: RedisClient,
    ) -> UserOut:
        if await self.user_repository.email_exists(email):
            raise BadRequestException("Email already exists", "email_exists")

        redis_otp = await redis_client.get(email)
        if not redis_otp or int(redis_otp) != verify_code_in:
            raise UnProcessableEntityException(
                loc=["body", "verify_code"], type="wrong_verify_code"
            )
        await redis_client.delete(email)

        hashed_password = self.password_handler.get_hashed(password)
        user = await self.user_repository.create_user(
            email=email, password=hashed_password, full_name=full_name
        )
        return UserOut(
            id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            full_name=user.full_name,
        )

    async def login_user(self, email: str, password: str) -> TokenOut:
        user = await self.user_repository.get_by_email(email)
        if not user or not self.password_handler.verify(password, user.password):
            raise BadRequestException("Wrong Credentials", "wrong_credentials")

        payload_access = {"user_id": user.id, "is_admin": user.is_admin}
        access_token = self.jwt_handler.encode_access_token(payload_access)

        payload_refresh = {"refresh_user_id": user.id}
        refresh_token = self.jwt_handler.encode_refresh_token(payload_refresh)
        return TokenOut(access_token=access_token, refresh_token=refresh_token)

    async def get_access_by_refresh_token(self, refresh_token: str) -> TokenOut:
        try:
            payload = self.jwt_handler.decode_refresh(token=refresh_token)
        except (JwtTokenExpiredException, BadJwtTokenException):
            raise UnAuthorizedException("token is invalid", "invalid_token")

        user_id = payload.get("refresh_user_id")
        user = await self.user_repository.get_by_id(user_id)

        payload_access = {"user_id": user_id, "is_admin": user.is_admin}
        access_token = self.jwt_handler.encode_access_token(payload_access)
        return TokenOut(access_token=access_token)
