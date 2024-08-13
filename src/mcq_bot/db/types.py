from typing import Literal, TypedDict, get_args

AnswerKeys = Literal["A", "B", "C", "D", "E"]
VALID_ANSWER_KEYS: list[AnswerKeys] = list(get_args(AnswerKeys))


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
