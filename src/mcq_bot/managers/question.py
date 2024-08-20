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
    def get_question_count(cls, s: Session, filename: str | None = None):
        """Get the number of questions for a Filename.path, or all if None."""
        query = select(func.count()).select_from(Question)
        if filename:
            query = query.join(Filename).where(Filename.path == filename)
        result = s.scalar(query)
        if not result:
            raise ValueError
        return result

    @classmethod
    @with_session
    def get_random_question(cls, s: Session, user_id: int, filename: str | None = None):
        """
        Return a random question, which has not been attempted by the user or which was incorrect, optionally filtering by a filename.

        If there are no unattempted questions, returns None.
        """
        attempted_correct_qn_ids = (
            select(Answer.question_id)
            .where(Attempt.user_id == user_id)
            .where(Answer.id == Attempt.answer_id)
            .where(Answer.is_correct)
        )

        stmt = (
            select(Question)
            .where(Question.id.not_in(attempted_correct_qn_ids))
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
