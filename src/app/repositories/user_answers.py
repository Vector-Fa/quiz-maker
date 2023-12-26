from pydantic import PositiveInt
from sqlalchemy import (
    select,
    update,
    case,
)
from sqlalchemy.orm import joinedload

from src.app.schemas.in_.quizzes import (
    UserDescriptiveAnswersIn,
)
from src.core.repository.base import BaseRepository
from src.app.models.quizzes.user_answers import (
    UserDescriptiveAnswer,
    UserMultipleOptionAnswer,
)


class UserAnswersRepository(BaseRepository[UserDescriptiveAnswer]):
    async def get_participant_descriptive(
        self, participant_id: int, descriptive_ids: list[int]
    ) -> list[UserDescriptiveAnswer]:
        query = (
            select(UserDescriptiveAnswer)
            .where(
                (UserDescriptiveAnswer.participant_id == participant_id)
                & (UserDescriptiveAnswer.id.in_(descriptive_ids))
            )
            .options(joinedload(UserDescriptiveAnswer.question))
        )
        return await self._all(query)

    async def update_user_descriptive_answer(
        self,
        descriptive_in: dict[PositiveInt, UserDescriptiveAnswersIn],
        descriptive_objects: list[UserDescriptiveAnswer],
    ) -> None:
        """
        Update participant answers, validating their existence and ensuring
        the entered score does not exceed the question score.
        """
        for descriptive_db in descriptive_objects:
            user_input = descriptive_in.get(descriptive_db.id)
            if user_input and user_input.score <= descriptive_db.question.score:
                descriptive_db.score = user_input.score
        await self.session.commit()

    async def update_multiple_option_answers(
        self, participant_id: int, ids: list[int]
    ):
        query = (
            update(UserMultipleOptionAnswer)
            .where(
                (UserMultipleOptionAnswer.participant_id == participant_id)
                & (UserMultipleOptionAnswer.id.in_(ids))
            )
            .values(
                is_correct=case(
                    (UserMultipleOptionAnswer.is_correct == True, False), else_=True  # noqa: E712
                )
            )
        )
        a = await self.session.execute(query)
        await self.session.commit()
        return a.rowcount

