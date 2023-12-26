from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from src.app.models import Question
from src.core.database import TimeStampedBase, Base


class Participant(TimeStampedBase):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    descriptive: Mapped[list["UserDescriptiveAnswer"]] = relationship()
    multiple_options: Mapped[list["UserMultipleOptionAnswer"]] = relationship()


class UserDescriptiveAnswer(Base):
    __tablename__ = "user_descriptive_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer: Mapped[str] = mapped_column(String(800))
    score: Mapped[float] = mapped_column(default=0)

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    question: Mapped["Question"] = relationship()


class UserMultipleOptionAnswer(Base):
    __tablename__ = "user_multiple_option_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_correct: Mapped[bool | None] = mapped_column(default=None)

    option_id: Mapped[int] = mapped_column(
        ForeignKey("multiple_options.id", ondelete="CASCADE")
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
