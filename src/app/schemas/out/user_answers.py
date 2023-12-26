from pydantic import BaseModel, PositiveInt, TypeAdapter, ConfigDict, Field

from src.app.models.enums_ import QuestionType


# ====-----====


class UserDescriptiveAnswersOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    score: float
    question_type: QuestionType = QuestionType.DESCRIPTIVE_SHORT_ANSWER
    question_id: PositiveInt
    answer: str


class UserMultipleOptionAnswersOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    is_correct: bool | None
    question_type: QuestionType = QuestionType.MULTIPLE_OPTIONS
    question_id: PositiveInt
    option_id: PositiveInt


class ParticipantAnswersOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    id: int = Field(..., serialization_alias="participant_id")
    descriptive: list[UserDescriptiveAnswersOut]
    multiple_options: list[UserMultipleOptionAnswersOut]


UserAnswersOutList = TypeAdapter(list[ParticipantAnswersOut])
# ====-----====
