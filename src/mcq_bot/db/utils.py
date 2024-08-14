import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .connection import get_engine
from .db_types import ProcessedRow
from .parsers.utils import validate_only_one_correct_answer
from .schema import Answer, Base, Filename, Question

logger = logging.getLogger(__file__)


def create_tables(checkfirst=True):
    Base.metadata.create_all(get_engine(), checkfirst=checkfirst)


def _add_filename_if_not_exists(sess: Session, filename: str) -> int:
    filename_id = sess.execute(
        select(Filename.id).where(Filename.path == filename)
    ).scalar()
    if not filename_id:
        filename_orm = Filename(path=filename)
        sess.add(filename_orm)
        sess.flush()
        filename_id = filename_orm.id
        logger.info("Added filename '%s' to db", filename)
    return filename_id


def _add_question(
    sess: Session, question_text: str, explanation: str, filename_id: int
):
    question = Question(
        text=question_text, explanation=explanation, filename_id=filename_id
    )
    sess.add(question)
    sess.flush()
    return question


def _get_question_by_text(sess: Session, text: str):
    sess.rollback()
    question = sess.scalar(select(Question).where(Question.text == text))
    return question


def add_question_and_answers(row: ProcessedRow, filename: str):
    """
    Add questions from ProcessedRows to the database. Duplicate questions are detected by identical question_texts and explanations.

    Returns True if the question was added, else False (if it was a duplicate)
    """
    question_text = row["question"]["text"]
    explanation = row["question"]["explanation"]
    answers = row["answers"]

    with Session(get_engine()) as s:
        filename_id = _add_filename_if_not_exists(s, filename)
        try:
            question = _add_question(s, question_text, explanation, filename_id)

            for answer_type in answers:
                answer = Answer(question=question, **answer_type)
                s.add(answer)

            validate_only_one_correct_answer(answers)

            s.commit()

            logger.info(
                "Added question %s... and %s answers to db",
                question_text[:20],
                len(answers),
            )
            return True
        except IntegrityError as e:
            duplicate_question = _get_question_by_text(s, question_text)
            if not duplicate_question:
                raise e

            logger.warn(
                "Skipped adding question '%s' in '%s' - already exists in '%s' ",
                question_text,
                filename,
                duplicate_question.filename.path,
            )
            return False
