from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    NonNegativeInt,
    PositiveInt,
    TypeAdapter,
    ConfigDict,
    Field,
    AliasPath,
)

from src.app.models.enums_ import QuestionType


class QuizInfoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    title: str


class CreatedQuizOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_info: QuizInfoOut = Field(..., validation_alias="Quiz")
    question_count: NonNegativeInt = 0


CreatedQuizOutList = TypeAdapter(list[CreatedQuizOut])


# ====-----====
class DescriptiveAnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    answer: str | None


class DescriptiveQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    question: str = Field(..., validation_alias="text")
    score: float
    question_type: QuestionType
    answer: DescriptiveAnswerOut | None = Field(None, validation_alias="descriptive")


# ====-----====
class MultipleOptionAnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str


MultipleOptionAnswerOutList = TypeAdapter(list[MultipleOptionAnswerOut])


class MultipleOptionQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    question: str = Field(..., validation_alias="text")
    score: float
    question_type: QuestionType
    choices: list[MultipleOptionAnswerOut] = Field(
        ..., validation_alias="multiple_options"
    )


# ====-----====


class DescriptiveQuestionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str
    question_type: Literal[
        QuestionType.DESCRIPTIVE_LONG_ANSWER, QuestionType.DESCRIPTIVE_SHORT_ANSWER
    ]
    score: float
    answer: DescriptiveAnswerOut | None = Field(None, validation_alias="descriptive")


class MultipleOptionQuestionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str
    question_type: Literal[QuestionType.MULTIPLE_OPTIONS]
    score: float
    choices: list[MultipleOptionAnswerOut] = Field(validation_alias="multiple_options")
    correct_option_id: PositiveInt = Field(
        validation_alias=AliasPath("correct_option", "option_id")
    )


class QuestionsOut(BaseModel):
    quiz_id: PositiveInt
    questions: list[MultipleOptionQuestionsOut | DescriptiveQuestionsOut] = Field(
        discriminator="question_type"
    )


# ====-----====
class QuizSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_id: int = Field(..., validation_alias="id")
    title: str
    start_at: datetime | None
    end_at: datetime | None
    is_active: bool
    shuffle_options: bool
    quiz_path: str
    password: str | None
    need_password: bool


# ====-----====


class QuizActivationStatus(BaseModel):
    message: str
    is_active: bool


# ====-----====


class QuizIsNotActiveOut(BaseModel):
    message: str
    start_at: datetime


# ====-----====


class PublishedDescriptiveQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str
    score: float
    question_type: Literal[
        QuestionType.DESCRIPTIVE_LONG_ANSWER, QuestionType.DESCRIPTIVE_SHORT_ANSWER
    ]


class PublishedChoicesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str


class PublishedMultipleOptionQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    text: str
    score: float
    question_type: Literal[QuestionType.MULTIPLE_OPTIONS]

    choices: list[PublishedChoicesOut] = Field(validation_alias="multiple_options")


class PublishedQuizQuestionsOut(BaseModel):
    quiz_id: PositiveInt
    quiz_title: str
    end_at: datetime
    questions: list[
        PublishedMultipleOptionQuestionOut | PublishedDescriptiveQuestionOut
    ] = Field(discriminator="question_type")


# ====-----====


class ParticipantsAnswersWithScoreOut(BaseModel):
    username: str
    participant_id: PositiveInt
    descriptive_score: float
    options_score: float


UserAnswersWithScoreOutList = TypeAdapter(list[ParticipantsAnswersWithScoreOut])


class ParticipantsAnswersOut(BaseModel):
    total_quiz_score: float
    participant_answers: list[ParticipantsAnswersWithScoreOut]


# ====-----====


class QuizPasswordStatus(BaseModel):
    quiz_id: PositiveInt
    need_password: bool


# ====-----====


class CorrectOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    correct_option_id: PositiveInt = Field(
        ..., validation_alias=AliasPath("correct_option", "option_id")
    )
    question_type: Literal[QuestionType.MULTIPLE_OPTIONS]
    score: float


class QuestionsByIdOut(BaseModel):
    questions: dict[PositiveInt, CorrectOptionOut | DescriptiveQuestionsOut] = Field(
        discriminator="question_type"
    )
