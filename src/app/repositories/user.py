from sqlalchemy import select, exists

from src.core.repository.base import BaseRepository

from ..models import User


class UserRepository(BaseRepository[User]):
    async def email_exists(self, email: str) -> bool:
        query = select(exists(select(User).where(User.email == email)))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, id_: int) -> User:
        query = self._get_by("id", id_)
        return await self._one(query)

    async def create_user(self, **kwargs) -> User:
        new_user = await self._create_and_refresh(**kwargs)
        return new_user

    async def get_by_email(self, email: str) -> User | None:
        query = self._get_by("email", email)
        return await self._one_or_none(query)
