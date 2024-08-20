import logging
from datetime import datetime
from typing import Sequence

from mcq_bot.db.schema import Answer, Attempt, Filename, Question
from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from .base import BaseManager
from .utils import with_session

_logger = logging.getLogger(__name__)


class AttemptManager(BaseManager):
    @classmethod
    @with_session
    def add_or_update_user_attempt(cls, s: Session, user_id: int, answer_id: int):
        attempt = s.scalar(
            select(Attempt)
            .where(Attempt.user_id == user_id)
            .where(Attempt.answer_id == answer_id)
        )
        if not attempt:
            attempt = Attempt(user_id=user_id, answer_id=answer_id)
            s.add(attempt)
            s.commit()
            _logger.info("Added attempt for user %s, answer_id %s", user_id, answer_id)

    @classmethod
    def _get_stats_query(cls) -> Select[tuple[bool, str, datetime, int]]:
        """
        Return a query consisting of:
        ```
        {
            Answer.is_correct,
            Filename.path,
            Attempt.attempt_dt,
            Attempt.user_id,
        }
        ```
        """
        return (
            select(
                Answer.is_correct,
                Filename.path,
                Attempt.attempt_dt,
                Attempt.user_id,
            )
            .join_from(Attempt, Answer)
            .join_from(Answer, Question)
            .join_from(Question, Filename)
        )

    @classmethod
    @with_session
    def get_attempted(cls, s: Session, user_id: int, only_correct: bool = False) -> int:
        """Returns the number of questions a user has attempted.

        only_correct: Whether to return only questions where the user has gotten them correct (default False).
        """
        query = (
            select(func.count(Question.id.distinct()))
            .select_from(Attempt)
            .join_from(Attempt, Answer)
            .join_from(Answer, Question)
            .where(Attempt.user_id == user_id)
        )
        if only_correct:
            query = query.where(Answer.is_correct)

        result = s.scalar(query)
        if not result:
            raise ValueError
        return result

    @classmethod
    @with_session
    def get_attempt_stats(
        cls,
        s: Session,
        user_id: int | None = None,
        filename: str | None = None,
        since_dt: datetime | None = None,
    ) -> Sequence[Row[tuple[bool, str, datetime, int]]]:
        """
        Return a list of
        ```
        {
            Answer.is_correct,
            Filename.path,
            Attempt.attempt_dt,
            Attempt.user_id,
        }
        ```

        `user_id`: User.id to filter by, or None for all.
        `filename`: Filename.path to filter by, or None for all.
        `since_days`: Number of days to look back (inclusive), or None for all. Note that this is in UTC.
        """
        query = cls._get_stats_query()
        if user_id:
            query = query.where(Attempt.user_id == user_id)
        if filename:
            query = query.where(Filename.path == filename)
        if since_dt:
            query = query.where(Attempt.attempt_dt >= since_dt)
        return s.execute(query).fetchall()
