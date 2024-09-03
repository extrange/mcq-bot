import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from mcq_bot.db.connection import get_engine
from mcq_bot.db.db_types import ProcessedRow
from mcq_bot.db.parsers.base import BaseParser
from mcq_bot.db.parsers.excel import ExcelParser
from mcq_bot.db.schema import Base
from mcq_bot.managers.question import QuestionManager
from mcq_bot.utils.logger import setup_logging

_logger = logging.getLogger(__name__)


class FileSummary(TypedDict):
    total: int
    added: int
    duplicate: int


def _log_summary(summary: dict[str, FileSummary]):
    for file in summary.keys():
        added = summary[file]["added"]
        duplicate = summary[file]["duplicate"]
        _logger.info(
            "Processed %s with %s expected questions", file, summary[file]["total"]
        )
        _logger.info(
            "%s added, %s duplicates - total processed: %s",
            added,
            duplicate,
            added + duplicate,
        )


def _process_files(
    files: list[Path], parser: BaseParser
) -> list[tuple[str, list[ProcessedRow]]]:
    """Run parser over all the provided files."""
    processed_files = []
    for file in files:
        processed_rows = parser.parse(file)
        processed_files.append((file.name, processed_rows))
        _logger.info(
            "Processed %s (%s questions) successfully", str(file), len(processed_rows)
        )
    return processed_files


def process_folder(folder: Path, parser: BaseParser) -> dict[str, FileSummary]:
    """Parse a folder containing questions (recursively) with the provided Parser, then adds to DB."""
    summary: dict[str, FileSummary] = defaultdict(
        lambda: {"total": 0, "added": 0, "duplicate": 0}
    )

    # Recursive
    files = list(folder.glob("**/*.xlsx"))
    processed_files = _process_files(files, parser)
    for filename, rows in processed_files:
        summary[filename]["total"] = len(rows)
        result = QuestionManager.bulk_add(rows, filename)
        summary[filename]["added"] = len(result["added"])
        summary[filename]["duplicate"] = len(result["duplicate"])
    _logger.info("Processed %s files successfully", len(files))

    # Add to DB
    return summary


def _make_path_absolute(path: Path) -> Path:
    return path if path.is_absolute() else path.absolute()


if __name__ == "__main__":
    setup_logging()

    if len(sys.argv) < 2:
        _logger.error(
            "You must supply a folder where questions will be added (recursively)",
        )
        sys.exit()

    # Create DB tables if they didn't exist
    Base.metadata.create_all(get_engine())

    questions_path = _make_path_absolute(Path(sys.argv[1]))

    result = process_folder(questions_path, ExcelParser())

    _log_summary(result)
