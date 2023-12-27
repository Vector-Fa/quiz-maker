import asyncio

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient

from src.core.cache.redis_client import get_redis
from src.core.auth.email_client import get_email_sender
from src.core.database import get_session
from src.core.server import create_app
from tests.extra.create_question import create_questions
from tests.extra.quizzes import update_quiz_date_times
from tests.extra.register_users import create_users_in_db
from tests.mocks import (
    get_mock_email_sender,
    MockRedis,
    mock_init_models,
    mock_get_session,
)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def app() -> FastAPI:
    app_ = create_app()
    await mock_init_models()
    app_.dependency_overrides[get_email_sender] = get_mock_email_sender
    app_.dependency_overrides[get_session] = mock_get_session
    app_.dependency_overrides[get_redis] = lambda: MockRedis()
    await create_users_in_db(app_)
    return app_


@pytest_asyncio.fixture(scope="function")
async def http_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as httpx_client:
        yield httpx_client


@pytest_asyncio.fixture(scope="session")
async def user_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as httpx_client:
        user_data = {"email": "user1@gmail.com", "password": "SomeStrongPassword@"}
        response = await httpx_client.post("/user/login", json=user_data)
        assert response.status_code == 200
        httpx_client.headers.update(
            {"Authorization": f'Bearer {response.json()["access_token"]}'}
        )
        yield httpx_client


@pytest_asyncio.fixture(scope="session")
async def user_client_2(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as httpx_client:
        user_data = {"email": "user2@gmail.com", "password": "SomeStrongPassword@"}
        response = await httpx_client.post("/user/login", json=user_data)
        assert response.status_code == 200
        httpx_client.headers.update(
            {"Authorization": f'Bearer {response.json()["access_token"]}'}
        )
        yield httpx_client


@pytest_asyncio.fixture(scope="function")
async def new_quiz(user_client: AsyncClient) -> dict:
    quiz_data = {"title": "my new quiz for user 1"}
    response = await user_client.post("/quiz/create", json=quiz_data)
    assert response.status_code == 200
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def quiz_another_user(user_client_2: AsyncClient) -> dict:
    quiz_data = {"title": "my new quiz for user 2"}
    response = await user_client_2.post("/quiz/create", json=quiz_data)
    assert response.status_code == 200
    return response.json()


@pytest_asyncio.fixture(scope="class")
async def shared_quiz(user_client: AsyncClient) -> dict:
    quiz_data = {"title": "shared quiz among tests"}
    response = await user_client.post("/quiz/create", json=quiz_data)
    assert response.status_code == 200
    quiz = response.json()

    await create_questions(quiz_id=quiz["id"], user_client=user_client)
    await update_quiz_date_times(user_client=user_client, quiz_id=quiz["id"])

    response = await user_client.post(f'/quiz/{quiz["id"]}/change-activation-status')
    assert response.status_code == 200

    response = await user_client.get(f'/quiz/{quiz["id"]}')
    return response.json()
