from datetime import date

from mcq_bot.db.schema import User
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session


class UserManager(BaseManager):
    @classmethod
    @with_session
    def add_user(cls, s: Session, user_id: int, exam_dt: date):
        user = s.scalar(select(User).where(User.id == user_id))
        if not user:
            user = User(id=user_id, exam_dt=exam_dt)
            s.add(user)
            s.flush()

        user.exam_dt = exam_dt
        s.commit()
        return user

    @classmethod
    @with_session
    def get_user(cls, s: Session, user_id: int) -> User:
        result = s.scalar(select(User).where(User.id == user_id))
        if not result:
            raise ValueError
        return result

    @classmethod
    @with_session
    def get_scheduled_users(cls, s: Session, exclude_exam_over=True):
        stmt = select(User).where(User.is_scheduled)
        if exclude_exam_over:
            today = date.today()
            stmt = stmt.where(User.exam_dt > today)

        return s.scalars(stmt).fetchall()
