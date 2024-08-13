from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import func

from .connection import get_engine


class Base(DeclarativeBase): ...


class Question(Base):
    __tablename__ = "question"

    # Prevent duplicate questions by checking both columns
    # Checking text alone is insufficient as some questions are similar
    # E.g. "Which of the following are false:"
    __table_args__ = (UniqueConstraint("text", "explanation"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    filename_id: Mapped[int] = mapped_column(ForeignKey("filename.id"))
    added_dt: Mapped[datetime] = mapped_column(server_default=func.now())
    explanation: Mapped[str | None]

    # Relationships
    filename: Mapped["Filename"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answer"

    # At most one answer per answer key (A, B, C, etc)
    __table_args__ = (UniqueConstraint("key", "question_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    is_correct: Mapped[bool]
    key: Mapped[int]  # A=0, B=1, etc
    text: Mapped[str]

    # Relationships
    question: Mapped[Question] = relationship(back_populates="answers")


class Filename(Base):
    __tablename__ = "filename"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(unique=True)
    questions: Mapped[list[Question]] = relationship(back_populates="filename")


class Attempt(Base):
    __tablename__ = "attempt"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id"),
        UniqueConstraint("user_id", "answer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answer.id"))
    attempt_dt: Mapped[datetime]


def _test_create(tables_to_drop: list[Base]):
    """
    Testing purposes. Drop all tables and recreate them.

    WILL DROP ALL TABLES
    """
    for t in tables_to_drop:
        try:
            t.__table__.drop(get_engine())  # type: ignore
        except Exception as e:
            print(e)
    Base.metadata.create_all(get_engine(), checkfirst=False)


def _dump_schema():
    from sqlalchemy.dialects import sqlite

    for m in [Question, Filename, Answer, Attempt]:
        print(CreateTable(m.__table__).compile(dialect=sqlite.dialect()))
