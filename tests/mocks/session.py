from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.database import Base, TimeStampedBase


mock_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
mock_async_session = async_sessionmaker(bind=mock_async_engine, expire_on_commit=False)


async def mock_init_models():
    async with mock_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def mock_get_session():
    try:
        async with mock_async_session() as session:
            yield session
    except SQLAlchemyError as e:
        print(e)
