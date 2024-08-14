from mcq_bot.db.schema import Answer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session


class AnswerManager(BaseManager):
    @classmethod
    @with_session
    def get_answer(cls, s: Session, answer_id: int):
        return s.scalar(select(Answer).where(Answer.id == answer_id))

    @classmethod
    @with_session
    def get_correct_answer(cls, s: Session, question_id: int):
        answer = s.scalar(
            select(Answer)
            .where(Answer.question_id == question_id)
            .where(Answer.is_correct)
        )
        if not answer:
            raise ValueError(f"No correct answer found for {question_id=}")
        return answer
