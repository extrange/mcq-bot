import logging
from typing import cast

from mcq_bot.db.db_types import ANSWER_INT_TO_LETTER
from mcq_bot.db.main import get_answer, get_correct_answer, get_question
from mcq_bot.db.schema import Answer, Question
from mcq_bot.senders.sender_types import AnswerCallback
from mcq_bot.utils.message import get_user_id, get_user_name
from telethon import events
from telethon.custom import Message

logger = logging.getLogger(__file__)


def _get_answered_qn(question: Question, answer: Answer):
    resp_str = f"Your answer: {ANSWER_INT_TO_LETTER[answer.key]}"
    feedback_str = (
        "✅"
        if answer.is_correct
        else f"❌\nCorrect answer: {ANSWER_INT_TO_LETTER[get_correct_answer(question.id).key]}"
    )
    explanation = question.explanation

    return f"{resp_str}{feedback_str}\n\n{explanation}"


async def handle_question_callback(event: events.CallbackQuery.Event):
    answer_cb = AnswerCallback.model_validate_json(event.data)
    question = get_question(answer_cb.question_id)
    answer = get_answer(answer_cb.answer_id)
    if not question or not answer:
        error = "Could not find question and/or answer"
        logger.error(error)
        raise ValueError(error)
    message = cast(Message, await event.get_message())
    username = await get_user_name(message)
    user_id = get_user_id(message)
    logging.info(
        "%s (%s) answered %s for question_id %s",
        username,
        user_id,
        answer.key,
        question.id,
    )

    answered_qn = _get_answered_qn(question, answer)

    await message.edit(text=str(message.text) + "\n\n" + answered_qn, buttons=None)
    await event.answer()
