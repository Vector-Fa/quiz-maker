from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.core.database import TimeStampedBase


class User(TimeStampedBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(length=50))
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    quizzes: Mapped["Quiz"] = relationship(back_populates="owner")
