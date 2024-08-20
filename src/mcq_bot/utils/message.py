from datetime import date
from typing import TypedDict, cast

from telethon.custom import Message
from telethon.types import User

from mcq_bot.managers.attempt import AttemptManager
from mcq_bot.managers.question import QuestionManager
from mcq_bot.managers.user import UserManager


def get_user_id(message: Message):
    user_id = message.sender_id
    if not user_id:
        raise Exception(f"No sender in message: {message.text=}")
    return user_id


async def get_user_name(message: Message):
    sender = cast(User, await message.get_sender())
    return sender.username


def extract_command_content(text: str):
    splits = text.split(" ", maxsplit=1)
    if len(splits) < 2:
        return None
    return splits[1]


class Stats(TypedDict):
    total: int
    attempted: int
    correct: int
    days_till_exam: int


def get_stats(user_id: int) -> Stats:
    """Obtain useful information about a user's question progress."""
    total = QuestionManager.get_question_count()
    attempted = AttemptManager.get_attempted(user_id)
    correct = AttemptManager.get_attempted(user_id, only_correct=True)
    exam_date = UserManager.get_user(user_id).exam_dt
    days_till_exam = exam_date - date.today()
    return {
        "attempted": attempted,
        "total": total,
        "correct": correct,
        "days_till_exam": days_till_exam.days,
    }


def format_stats_message(stats: Stats) -> str:
    """
    Return stat message to the user in the form of:
    ```
    Attempted: 4/1029 (10%)
    Correct: 2/4 (50%)

    Remaining: 939
    Days till exam: 20
    Questions to do per day: 30
    ```
    """
    percent_attempted = stats["attempted"] / stats["total"] * 100
    percent_correct = stats["correct"] / stats["attempted"] * 100
    remaining = stats["total"] - stats["attempted"]
    return (
        f"Attempted: **{stats["attempted"]} of {stats["total"]}** ({percent_attempted:.1f}%)\n"
        f"Correct: **{stats["correct"]} of {stats["attempted"]}** ({round(percent_correct)}%)\n"
        f"\n"
        f"Remaining: **{remaining}**\n"
        f"Days till exam: **{stats["days_till_exam"]}**\n"
        f"Questions to do per day: **{remaining/stats["days_till_exam"]:.0f}**"
    )
