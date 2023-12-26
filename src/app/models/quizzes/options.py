from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import TimeStampedBase, Base

# noqa: F821
class Descriptive(TimeStampedBase):
    __tablename__ = "descriptive"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer: Mapped[str | None] = mapped_column(String(600), default=None)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    question: Mapped["Question"] = relationship(back_populates="descriptive")


class MultipleOption(TimeStampedBase):
    __tablename__ = "multiple_options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str]

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    question: Mapped["Question"] = relationship(back_populates="multiple_options")


class CorrectOption(Base):
    __tablename__ = "correct_option"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    option_id: Mapped[int]

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
