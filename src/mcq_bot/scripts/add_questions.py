import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from mcq_bot.db.db_types import ProcessedRow
from mcq_bot.db.main import add_question_and_answers, create_tables
from mcq_bot.db.parsers.base import BaseParser
from mcq_bot.db.parsers.excel import ExcelParser
from mcq_bot.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class FileSummary(TypedDict):
    total: int
    added: int
    duplicate: int


def log_summary(summary: dict[str, FileSummary]):
    for file in summary.keys():
        added = summary[file]["added"]
        duplicate = summary[file]["duplicate"]
        logger.info(
            "Processed %s with %s expected questions", file, summary[file]["total"]
        )
        logger.info(
            "%s added, %s duplicates - total %s actually processed",
            added,
            duplicate,
            added + duplicate,
        )


def process_files(
    files: list[Path], parser: BaseParser
) -> list[tuple[str, list[ProcessedRow]]]:
    processed_files = []
    for file in files:
        processed_rows = parser.parse(file)
        processed_files.append((file.name, processed_rows))
        logger.info(
            "Processed %s (%s questions) successfully", str(file), len(processed_rows)
        )
    return processed_files


def main(folder: Path, parser: BaseParser):
    summary: dict[str, FileSummary] = defaultdict(
        lambda: {"total": 0, "added": 0, "duplicate": 0}
    )

    # Recursive
    files = list(folder.glob("**/*.xlsx"))
    processed_files = process_files(files, parser)
    for file, rows in processed_files:
        summary[file]["total"] = len(rows)
    logger.info("Processed %s files successfully", len(files))

    # Only continue if all files were formatted correctly

    create_tables()

    for filename, processed_rows in processed_files:
        for row in processed_rows:
            was_qn_added = add_question_and_answers(
                row,
                filename,
            )
            if was_qn_added:
                summary[filename]["added"] += 1
            else:
                summary[filename]["duplicate"] += 1

    log_summary(summary)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "You must supply a folder where questions will be added (recursively)",
            file=sys.stderr,
        )
        sys.exit()

    path = Path(sys.argv[1])

    path_with_cwd = path if path.is_absolute() else Path.cwd() / path

    main(Path(sys.argv[1]), ExcelParser())
