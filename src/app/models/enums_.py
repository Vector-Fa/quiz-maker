from enum import StrEnum, auto


class QuestionType(StrEnum):
    DESCRIPTIVE_LONG_ANSWER = auto()
    DESCRIPTIVE_SHORT_ANSWER = auto()
    MULTIPLE_OPTIONS = auto()
