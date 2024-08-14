from mcq_bot.db.schema import Attempt
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session


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
