import logging
from typing import Sequence

from mcq_bot.db.schema import Filename
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session

_logger = logging.getLogger(__name__)


class FilenameManager(BaseManager):
    @classmethod
    @with_session
    def fetch_all(cls, s: Session) -> Sequence[Filename]:
        """Fetch all filenames in the database."""
        return s.scalars(select(Filename)).fetchall()

    @classmethod
    @with_session
    def fetch_or_create(cls, s: Session, file_path: str) -> Filename:
        """Get a filename, or create it if it doesn't exist."""
        filename = s.execute(
            select(Filename).where(Filename.path == file_path)
        ).scalar()
        if not filename:
            filename_orm = Filename(path=file_path)
            s.add(filename_orm)
            s.commit()
            filename = filename_orm
            _logger.info("Added filename '%s' to db", file_path)
        return filename
