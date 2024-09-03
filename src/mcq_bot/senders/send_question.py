import logging

from mcq_bot.client import get_client
from mcq_bot.db.db_types import ANSWER_INT_TO_LETTER
from mcq_bot.db.schema import Answer, Question
from mcq_bot.managers.question import QuestionManager
from telethon import Button
from telethon.events import StopPropagation

from .sender_types import AnswerCallback

logger = logging.getLogger(__file__)


def _prepare_inline_buttons(answers: list[Answer], user_id: int):
    callbacks = [
        Button.inline(
            ANSWER_INT_TO_LETTER[ans.key],
            AnswerCallback(
                answer_id=ans.id, question_id=ans.question_id, user_id=user_id
            ).model_dump_json(),
        )
        for ans in answers
    ]
    return callbacks


def _format_question(question: Question):
    filename = question.filename.path
    qn_text = question.text
    answers = "\n\n".join(
        [f"<b>{ANSWER_INT_TO_LETTER[a.key]}.</b> {a.text}" for a in question.answers]
    )

    return f"<p>{qn_text}<p>\n\n{answers}\n\n<i>From {filename}</i>"


async def send_question(user_id: int):
    client = get_client()
    question = QuestionManager.fetch_random_single(user_id)
    if not question:
        await client.send_message(user_id, "You have answered all questions!")
        raise StopPropagation

    buttons = _prepare_inline_buttons(question.answers, user_id)
    message_text = _format_question(question)

    await client.send_message(user_id, message_text, buttons=buttons, parse_mode="html")
