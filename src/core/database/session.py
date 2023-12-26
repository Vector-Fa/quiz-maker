from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ..config import settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TimeStampedBase(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


async_engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    try:
        async with async_session() as session:
            yield session
    except SQLAlchemyError as e:
        print(e)
