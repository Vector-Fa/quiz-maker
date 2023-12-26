from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers import AuthController
from src.app.repositories import UserRepository
from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.extra.token import TokenOut, TokenData
from src.app.schemas.in_.users import (
    EmailRegisterIn,
    UserLoginIn,
    UserRegisterIn,
    RefreshTokenIn,
)
from src.app.schemas.out.users import UserOut
from src.core.cache.redis_client import RedisClient, get_redis
from src.core.auth.email_client import EmailClient, get_email_sender
from src.core.database import get_session
from src.core.fastapi.dependencies.auth import get_current_user, authentication_required


router = APIRouter()


@router.post("/register/send-code")
async def send_verify_code(
    user_email: EmailRegisterIn,
    background_tasks: BackgroundTasks,
    email_client: Annotated[EmailClient, Depends(get_email_sender)],
    redis_client: Annotated[RedisClient, Depends(get_redis)],
    db_session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    user_repository = UserRepository(db_session)
    return await AuthController(user_repository).send_verify_code(
        user_email=user_email.email,
        background_tasks=background_tasks,
        email_client=email_client,
        redis_client=redis_client,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserRegisterIn,
    redis_client: Annotated[RedisClient, Depends(get_redis)],
    db_session: AsyncSession = Depends(get_session),
) -> UserOut:
    user_repository = UserRepository(db_session)
    return await AuthController(user_repository).register_user(
        email=user.email,
        password=user.password,
        verify_code_in=user.verify_code,
        full_name=user.full_name,
        redis_client=redis_client,
    )


@router.post("/login")
async def login_user(
    user_in: UserLoginIn,
    db_session: AsyncSession = Depends(get_session),
) -> TokenOut:
    user_repository = UserRepository(db_session)
    return await AuthController(user_repository).login_user(
        email=user_in.email, password=user_in.password
    )


@router.get("/profile")
async def user_profile(
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await get_current_user(db_session, token.user_id)
    return UserOut.model_validate(user)


@router.post("/refresh/token")
async def refresh_token(
    token: RefreshTokenIn,
    db_session: AsyncSession = Depends(get_session),
) -> TokenOut:
    user_repository = UserRepository(db_session)
    return await AuthController(user_repository).get_access_by_refresh_token(
        refresh_token=token.refresh_token
    )
