from typing import Literal, TypedDict, get_args

AnswerKeys = Literal["A", "B", "C", "D", "E"]
VALID_ANSWER_LETTERS: list[AnswerKeys] = list(get_args(AnswerKeys))

ANSWER_LETTER_TO_INT = dict(zip(VALID_ANSWER_LETTERS, range(len(VALID_ANSWER_LETTERS))))

ANSWER_INT_TO_LETTER = {v: k for k, v in ANSWER_LETTER_TO_INT.items()}


class AnswerType(TypedDict):
    is_correct: bool
    key: int
    text: str


class QuestionType(TypedDict):
    text: str
    explanation: str


class ProcessedRow(TypedDict):
    question: QuestionType
    answers: list[AnswerType]


class NoCorrectAnswerException(Exception): ...


class UserNotFound(Exception): ...
