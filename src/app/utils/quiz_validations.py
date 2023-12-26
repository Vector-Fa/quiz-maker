from datetime import timezone, datetime

from src.app.models import Quiz
from src.core.excpetions import BadRequestException


def check_quiz_dates(start_at: datetime, end_at: datetime) -> None:
    current_date = datetime.now(tz=timezone.utc)
    if start_at:
        if current_date < start_at:
            raise BadRequestException("quiz not started", "quiz_not_started")
        elif current_date > end_at:
            raise BadRequestException("quiz is over", "quiz_ended")


def validate_quiz_for_activation(quiz: Quiz) -> None:
    if not quiz.end_at or not quiz.start_at:
        raise BadRequestException("dates are not present", "bad_dates")
    if not quiz.end_at > quiz.start_at:
        raise BadRequestException("wrong dates", "bad_dates")
    if len(quiz.questions) == 0:
        raise BadRequestException("quiz have no question", "quiz_have_no_question")
    if quiz.need_password and not quiz.password:
        raise BadRequestException("Add password to quiz", "set_quiz_password")


def validate_quiz_is_started(quiz: Quiz) -> None:
    check_quiz_dates(quiz.start_at, quiz.end_at)

    if not quiz.is_active:
        raise BadRequestException("quiz not active", "quiz_not_activated")
