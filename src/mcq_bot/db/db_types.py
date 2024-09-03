from typing import Literal, get_args

from pydantic import BaseModel

AnswerKeys = Literal["A", "B", "C", "D", "E"]
VALID_ANSWER_LETTERS: list[AnswerKeys] = list(get_args(AnswerKeys))

ANSWER_LETTER_TO_INT = dict(zip(VALID_ANSWER_LETTERS, range(len(VALID_ANSWER_LETTERS))))

ANSWER_INT_TO_LETTER = {v: k for k, v in ANSWER_LETTER_TO_INT.items()}


class AnswerType(BaseModel):
    is_correct: bool
    key: int
    text: str


class QuestionType(BaseModel):
    text: str
    explanation: str


class ProcessedRow(BaseModel):
    question: QuestionType
    answers: list[AnswerType]


class NoCorrectAnswerException(Exception): ...


class UserNotFound(Exception): ...
