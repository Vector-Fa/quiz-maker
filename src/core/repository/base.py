from typing import Generic, Type, TypeVar, Any, Sequence

from sqlalchemy import select, Select, Delete, delete, Result, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base
from src.core.excpetions.database import ItemNotFoundError

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    def __init__(self, model: Type[Model], db_session: AsyncSession):
        self.model = model
        self.session = db_session

    def _get_by(self, field: str, value: Any) -> Select:
        query = select(self.model).where(getattr(self.model, field) == value)  # noqa
        return query

    def _delete_by(self, field: str, value: Any) -> Delete:
        query = delete(self.model).where(getattr(self.model, field) == value)  # noqa
        return query

    async def _create_and_refresh(self, **kwargs) -> Model:
        new_model = self.model(**kwargs)
        self.session.add(new_model)
        await self.session.commit()
        await self.session.refresh(new_model)
        return new_model

    async def _create(self, **kwargs) -> None:
        new_model = self.model(**kwargs)
        self.session.add(new_model)
        await self.session.commit()

    async def _one(self, query) -> Model:
        result = await self.session.scalars(query)
        result = result.one_or_none()
        if not result:
            raise ItemNotFoundError
        return result

    async def _one_or_none(self, query) -> Model | None:
        result = await self._execute(query)
        return result.scalars().one_or_none()

    async def _all(self, query) -> list[Model]:
        results = await self.session.scalars(query)
        return results.all()

    async def _mappings_one(self, query) -> RowMapping:
        result = await self._execute(query)
        return result.mappings().one()

    async def _mappings_all(self, query) -> Sequence[RowMapping]:
        result = await self._execute(query)
        return result.mappings().all()

    async def _execute(self, query) -> Result[Any]:
        return await self.session.execute(query)
