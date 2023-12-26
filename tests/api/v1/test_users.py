import pytest
from httpx import AsyncClient


class TestUsers:
    @pytest.mark.asyncio
    async def test_send_verify_code_email(self, http_client: AsyncClient):
        email_data = {"email": "farhadbm2020@gmail.com"}
        response = await http_client.post("/user/register/send-code", json=email_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_wrong_email_for_verify_code(self, http_client: AsyncClient):
        email_data = {"email": "wrong"}
        response = await http_client.post("/user/register/send-code", json=email_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_profile(self, user_client: AsyncClient):
        response = await user_client.get("/user/profile")
        assert response.status_code == 200
