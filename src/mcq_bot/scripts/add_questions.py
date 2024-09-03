import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from mcq_bot.db.connection import get_engine
from mcq_bot.db.db_types import ProcessedRow
from mcq_bot.db.parsers.base import BaseParser
from mcq_bot.db.parsers.openai import OpenAiParser
from mcq_bot.db.schema import Base
from mcq_bot.managers.question import QuestionManager
from mcq_bot.utils.logger import setup_logging
from pydantic_core import from_json, to_jsonable_python

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


def _parse_files(
    files: list[Path], parser: type[BaseParser]
) -> list[tuple[str, list[ProcessedRow]]]:
    """Run parser over all the provided files."""
    processed_files = []
    for file in files:
        processed_rows = parser().parse(file)
        processed_files.append((file.name, processed_rows))
        _logger.info(
            "Parsed %s (%s questions) successfully", str(file), len(processed_rows)
        )
    return processed_files


def _process_rows(processed_rows: list[ProcessedRow], filename: str) -> FileSummary:
    """Adds a list[ProcessedRow] to the DB."""

    summary: FileSummary = {"total": 0, "added": 0, "duplicate": 0}

    summary["total"] = len(processed_rows)
    try:
        result = QuestionManager.bulk_add(processed_rows, filename)
        summary["added"] = len(result["added"])
        summary["duplicate"] = len(result["duplicate"])
    except Exception:
        _logger.exception("Failed to add questions for filename %s to DB:", filename)

    return summary


def process_folder(
    folder: Path, parser: type[BaseParser], save_dir: Path | None = None
) -> dict[str, FileSummary]:
    """Parse a folder containing questions (recursively) with the provided Parser, then adds to DB.

    If these are .xlsx files, they are parsed by the Parser.

    If they are .json files, then the stem is used for the filename, and the contents of the JSON file are expected to be list[ProcessedRow]."""
    summary: dict[str, FileSummary] = defaultdict(
        lambda: {"total": 0, "added": 0, "duplicate": 0}
    )

    # Recursive
    xlsx_files = list(folder.glob("**/*.xlsx"))
    json_files = list(folder.glob("**/*.json"))

    processed_xlsx = _parse_files(xlsx_files, parser)

    if save_dir:
        save_dir.mkdir(exist_ok=True)
        for processed_file in processed_xlsx:
            with (save_dir / f"{processed_file[0]}.json").open("w") as f:
                json.dump(to_jsonable_python(processed_file[1]), f, indent=2)

    # .xlsx
    for filename, processed_rows in processed_xlsx:
        summary[filename] = _process_rows(processed_rows, filename)

    # .json
    for file in json_files:
        with file.open("r") as f:
            json_data: list = from_json(f.read())
            processed_rows = [ProcessedRow.model_validate(m) for m in json_data]
            summary[file.stem] = _process_rows(processed_rows, file.stem)

    _logger.info("Processed %s .xlsx files", len(xlsx_files))
    _logger.info("Processed %s .json files", len(json_files))

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
    save_dir = _make_path_absolute(Path(sys.argv[2]))

    result = process_folder(questions_path, OpenAiParser, save_dir)

    _log_summary(result)
