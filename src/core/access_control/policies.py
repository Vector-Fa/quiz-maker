
from src.app.models import Quiz
from src.core.excpetions import ForbiddenException
from src.core.protocols.user_info import UserInfo


async def is_quiz_owner(kwargs: dict) -> bool:
    """check whether user is the quiz owner"""
    user_info: UserInfo = kwargs["user_info"]
    quiz: Quiz = kwargs["quiz"]

    if quiz.owner_id != user_info.user_id:
        raise ForbiddenException("You are not quiz owner", "user_not_quiz_owner")
    return True


async def is_admin(kwargs: dict) -> bool:
    user_info: UserInfo = kwargs["user_info"]
    return user_info.is_admin


async def check_quiz_password(kwargs: dict) -> bool:
    quiz: Quiz = kwargs["quiz"]
    if quiz.need_password and quiz.password:
        if quiz.password != kwargs["entered_password"]:
            raise ForbiddenException(
                "quiz password is not correct", "wrong_quiz_password"
            )
    return True
