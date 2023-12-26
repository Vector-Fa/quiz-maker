from sqlalchemy import select, func, case, MappingResult
from sqlalchemy.orm import selectinload

from src.app.models import Question
from src.app.models.quizzes.user_answers import (
    Participant,
    UserDescriptiveAnswer,
    UserMultipleOptionAnswer,
)
from src.app.schemas.in_.quizzes import (
    UserMultipleOptionAnswersIn,
    UserDescriptiveAnswersIn,
)
from src.core.repository.base import BaseRepository


class ParticipantRepo(BaseRepository[Participant]):
    async def add_participant_info_with_answers(
        self,
        username: str,
        quiz_id: int,
        multiple_option_answers: list[UserMultipleOptionAnswersIn],
        descriptive_answers: list[UserDescriptiveAnswersIn],
    ):
        participant_info = Participant(username=username, quiz_id=quiz_id)
        participant_info.descriptive = [
            UserDescriptiveAnswer(answer=a.answer, question_id=a.question_id)
            for a in descriptive_answers
        ]
        participant_info.multiple_options = [
            UserMultipleOptionAnswer(option_id=a.option_id, question_id=a.question_id)
            for a in multiple_option_answers
        ]
        self.session.add(participant_info)
        await self.session.commit()

    async def get_participants_with_answers(self, quiz_id: int) -> list[Participant]:
        query = (
            select(Participant)
            .options(
                selectinload(Participant.descriptive),
                selectinload(Participant.multiple_options),
            )
            .where(Participant.quiz_id == quiz_id)
        )
        return await self._all(query)

    async def get_participant_answers_with_score(self, quiz_id: int) -> MappingResult:
        """
        group all participants for a quiz and calculate their current score on the quiz
        """
        subquery_descriptive_answers = (
            select(
                UserDescriptiveAnswer.participant_id,
                func.sum(UserDescriptiveAnswer.score).label("descriptive_score"),
            )
            .group_by(UserDescriptiveAnswer.participant_id)
            .subquery()
        )
        subquery_multiple_option = (
            select(
                UserMultipleOptionAnswer.participant_id,
                func.sum(
                    case((UserMultipleOptionAnswer.is_correct == True, Question.score))  # noqa: E712
                ).label("options_score"),
            )
            .join(Question, Question.id == UserMultipleOptionAnswer.question_id)
            .group_by(UserMultipleOptionAnswer.participant_id)
            .subquery()
        )
        query = (
            select(
                Participant.username,
                Participant.id.label("participant_id"),
                func.coalesce(
                    func.sum(subquery_descriptive_answers.c.descriptive_score), 0
                ).label("descriptive_score"),
                func.coalesce(
                    func.sum(subquery_multiple_option.c.options_score), 0
                ).label("options_score"),
            )
            .select_from(Participant)
            .outerjoin(
                subquery_descriptive_answers,
                subquery_descriptive_answers.c.participant_id == Participant.id,
            )
            .outerjoin(
                subquery_multiple_option,
                subquery_multiple_option.c.participant_id == Participant.id,
            )
            .where(Participant.quiz_id == quiz_id)
            .group_by(Participant.username, Participant.id)
        )
        results = await self._execute(query)
        return results.mappings()

    async def get_participant_with_answers(
        self, quiz_id: int, participant_id: int
    ) -> Participant:
        query = (
            select(Participant)
            .options(
                selectinload(Participant.descriptive),
                selectinload(Participant.multiple_options),
            )
            .where(
                (Participant.quiz_id == quiz_id) & (Participant.id == participant_id)
            )
        )
        return await self._one(query)
