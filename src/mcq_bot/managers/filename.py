from mcq_bot.db.schema import Filename
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session


class FilenameManager(BaseManager):
    @classmethod
    @with_session
    def get_filenames(cls, s: Session):
        return s.scalars(select(Filename)).fetchall()
