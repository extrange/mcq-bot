import logging
from typing import TypedDict

from mcq_bot.db.db_types import ProcessedRow
from mcq_bot.db.schema import Answer, Attempt, Filename, Question
from mcq_bot.managers.filename import FilenameManager
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .base import BaseManager
from .utils import with_session

_logger = logging.getLogger(__name__)


class BulkAddResult(TypedDict):
    added: list[ProcessedRow]
    duplicate: list[ProcessedRow]


class QuestionManager(BaseManager):
    @classmethod
    @with_session
    def by_answer_id(cls, s: Session, answer_id: int) -> Question | None:
        """Fetch a question with the matching answer_id."""
        return s.scalar(select(Answer.question).where(Answer.id == answer_id))

    @classmethod
    @with_session
    def by_text(cls, s: Session, text: str) -> Question | None:
        """Fetch a question with the matching text."""
        question = s.scalar(select(Question).where(Question.text == text))
        return question

    @classmethod
    @with_session
    def fetch(cls, s: Session, question_id: int) -> Question | None:
        """Get the question with the id."""
        return s.scalar(select(Question).where(Question.id == question_id))

    @classmethod
    @with_session
    def count(cls, s: Session, filename: str | None = None) -> int:
        """Get the number of questions for a Filename.path, or of all if None."""
        query = select(func.count()).select_from(Question)
        if filename:
            query = query.join(Filename).where(Filename.path == filename)
        result = s.scalar(query)
        if not result:
            raise ValueError
        return result

    @classmethod
    @with_session
    def fetch_random_single(cls, s: Session, user_id: int, filename: str | None = None):
        """
        Return a random question, which has not been attempted by the user or which was incorrect, optionally filtering by a filename.

        If there are no unattempted questions, returns None.
        """
        attempted_correct_qn_ids = (
            select(Answer.question_id)
            .where(Attempt.user_id == user_id)
            .where(Answer.id == Attempt.answer_id)
            .where(Answer.is_correct)
        )

        stmt = (
            select(Question)
            .where(Question.id.not_in(attempted_correct_qn_ids))
            .order_by(func.random())
            .limit(1)
        )
        if filename:
            filename_id = (
                select(Filename.id).where(Filename.path == filename).scalar_subquery()
            )
            stmt = stmt.where(Question.filename_id == filename_id)

        qn = s.scalar(stmt)
        return qn

    @classmethod
    @with_session
    def add(
        cls, s: Session, question_text: str, explanation: str, filename_id: int
    ) -> Question:
        """Add a question to the database."""
        question = Question(
            text=question_text, explanation=explanation, filename_id=filename_id
        )
        s.add(question)
        s.commit()
        return question

    @classmethod
    @with_session
    def bulk_add(
        cls, s: Session, rows: list[ProcessedRow], filename: str
    ) -> BulkAddResult:
        """
        Add questions from ProcessedRows (the result of a Parser) with the given filename to the database, in a single transaction.

        Returns a dict of added and skipped (duplicated) ProcessedRows.
        """

        summary: BulkAddResult = {"added": [], "duplicate": []}

        filename_orm = FilenameManager.fetch_or_create(filename)

        for row in rows:
            answers = row.answers
            question_text = row.question.text
            question = Question(
                text=question_text,
                explanation=row.question.explanation,
                filename_id=filename_orm.id,
            )

            try:
                s.add(question)
                s.flush()

            except IntegrityError:
                s.rollback()
                dup_question = s.scalar(
                    select(Question).where(Question.text == question_text)
                )
                if not dup_question:
                    raise ValueError(
                        f"Could not find question with text '{question_text}'"
                    )
                _logger.warning(
                    "Skipped adding question '%s' in '%s' - already exists in '%s' ",
                    question.text,
                    filename,
                    dup_question.filename,
                )
                summary["duplicate"].append(row)
                continue
            else:
                for answer_type in answers:
                    answer = Answer(
                        question=question,
                        is_correct=answer_type.is_correct,
                        key=answer_type.key,
                        text=answer_type.text,
                    )
                    s.add(answer)
                summary["added"].append(row)
                _logger.info(
                    "Added question %s... and %s answers to db",
                    question.text[:20],
                    len(answers),
                )

        s.commit()
        return summary
