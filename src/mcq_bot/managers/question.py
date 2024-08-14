from mcq_bot.db.schema import Answer, Attempt, Filename, Question
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session


class QuestionManager(BaseManager):
    @classmethod
    @with_session
    def get_question_by_answer(cls, s: Session, answer_id: int):
        return s.scalar(select(Answer.question).where(Answer.id == answer_id))

    @classmethod
    @with_session
    def get_question(cls, s: Session, question_id: int):
        return s.scalar(select(Question).where(Question.id == question_id))

    @classmethod
    @with_session
    def get_random_question(cls, s: Session, user_id: int, filename: str | None = None):
        """
        Return a random question, which has not been attempted by the user, optionally filtering by a filename.

        If there are no unattempted questions, returns None.
        """
        attempted_qn_ids = (
            select(Answer.question_id)
            .where(Attempt.user_id == user_id)
            .where(Answer.id == Attempt.answer_id)
        )

        stmt = (
            select(Question)
            .where(Question.id.not_in(attempted_qn_ids))
            .order_by(func.random())
            .limit(1)
        )
        if filename:
            filename_id = (
                select(Filename.id).where(Filename.path == filename).scalar_subquery()
            )
            stmt = stmt.where(Question.filename_id == filename_id)

        qn = s.scalar(stmt)
        return qn
