from abc import ABC, abstractmethod
from pathlib import Path

from mcq_bot.db.db_types import ProcessedRow


class BaseParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> list[ProcessedRow]:
        """
        Process questions and answers in a file and returns in a format suitable for adding to the database.

        Also strips out whitespace from question and answer text.
        """
