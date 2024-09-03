import pytest
from mcq_bot.db.connection import get_engine
from mcq_bot.db.db_types import AnswerType, ProcessedRow, QuestionType
from mcq_bot.db.schema import Base
from mcq_bot.managers.question import QuestionManager
from mcq_bot.utils.logger import setup_logging

_COUNT = 10


@pytest.fixture(autouse=True, scope="session")
def _setup_logging():
    setup_logging()


@pytest.fixture(autouse=True)
def _prepare_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def get_rows() -> list[ProcessedRow]:
    """Return a normal list of ProcessedRows."""
    return [
        ProcessedRow(
            question=QuestionType(
                text=f"test question {i}", explanation=f"explanation {i}"
            ),
            answers=[
                AnswerType(
                    text=f"answer {j} for question {i}",
                    key=j,
                    is_correct=True if j == 0 else False,
                )
                for j in range(5)
            ],
        )
        for i in range(_COUNT)
    ]


@pytest.fixture
def multiple_correct_answers() -> list[ProcessedRow]:
    """Return ProcessedRows with multiple correct answers"""
    return [
        ProcessedRow(
            question=QuestionType(
                text=f"test question {i}", explanation=f"explanation {i}"
            ),
            answers=[
                AnswerType(text=f"answer {j} for question {i}", key=j, is_correct=True)
                for j in range(5)
            ],
        )
        for i in range(_COUNT)
    ]


def test_bulk_add():
    QuestionManager.bulk_add(get_rows(), "test")
    assert QuestionManager.count() == _COUNT


def test_duplicate_question():
    """Check that duplicate questions with same question_text and explanations do not get added."""
    rows = get_rows()
    for _ in range(2):
        QuestionManager.bulk_add(rows, "test")
    assert QuestionManager.count() == _COUNT
