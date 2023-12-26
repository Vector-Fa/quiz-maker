from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import TimeStampedBase
from ..enums_ import QuestionType

from ..quizzes import Descriptive, MultipleOption, CorrectOption


class Question(TimeStampedBase):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str]
    question_type: Mapped[QuestionType] = mapped_column(
        ENUM(QuestionType, name="question_type"), name="question_type"
    )
    score: Mapped[float]

    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE")
    )
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    descriptive: Mapped["Descriptive"] = relationship(back_populates="question")
    multiple_options: Mapped[list["MultipleOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    correct_option: Mapped["CorrectOption"] = relationship()
