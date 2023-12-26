from fastapi import FastAPI
from httpx import AsyncClient

from ..mocks.email import MockEmail


async def register_users(http_client: AsyncClient, email: str):
    email_data = {"email": email}
    response = await http_client.post("/user/register/send-code", json=email_data)
    assert response.status_code == 200

    register_data = {
        "email": email,
        "full_name": "Test User",
        "password": "SomeStrongPassword@",
        "verify_code": MockEmail.get_verify_code(email=email),
    }
    response = await http_client.post("/user/register", json=register_data)
    assert response.status_code == 201


async def create_users_in_db(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as httpx_client:
        await register_users(httpx_client, email="user1@gmail.com")
        await register_users(httpx_client, email="user2@gmail.com")
