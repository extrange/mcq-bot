import logging
from typing import cast

from mcq_bot.db.db_types import ANSWER_INT_TO_LETTER
from mcq_bot.db.schema import Answer, Question
from mcq_bot.managers.answer import AnswerManager
from mcq_bot.managers.attempt import AttemptManager
from mcq_bot.managers.question import QuestionManager
from mcq_bot.senders.sender_types import AnswerCallback
from mcq_bot.utils.message import get_attempted_today, get_daily_target, get_user_name
from telethon import Button, events
from telethon.custom import Message
from telethon.events import StopPropagation

logger = logging.getLogger(__file__)


def _get_daily_target_prompt(user_id: int):
    target = get_daily_target(user_id)
    attempted = get_attempted_today(user_id)
    if attempted >= target:
        return (
            f"You've completed your target for today! ({attempted}/{target})\U0001f389"
        )
    remaining = target - attempted
    return f"{attempted} done so far, {remaining} to go!"


def _get_answered_qn(question: Question, answer: Answer):
    resp_str = f"Your answer: {ANSWER_INT_TO_LETTER[answer.key]}"
    feedback_str = (
        "✅"
        if answer.is_correct
        else f"❌\nCorrect answer: {ANSWER_INT_TO_LETTER[AnswerManager.get_correct_answer(question.id).key]}"
    )
    explanation = question.explanation

    return f"{resp_str}{feedback_str}\n\n{explanation}"


async def _log(message: Message, user_id: int, question_id: int, answer_key: int):
    username = await get_user_name(message)
    logging.info(
        "%s (%s) answered %s for question_id %s",
        username,
        user_id,
        answer_key,
        question_id,
    )


async def handle_question_callback(event: events.CallbackQuery.Event):
    answer_cb = AnswerCallback.model_validate_json(event.data)
    question = QuestionManager.get_question(answer_cb.question_id)
    answer = AnswerManager.get_answer(answer_cb.answer_id)

    # message.sender_id in this callback is that of the bot, not the user
    user_id = answer_cb.user_id

    if not question or not answer:
        error = "Could not find question and/or answer"
        logger.error(error)
        raise ValueError(error)

    message = cast(Message, await event.get_message())

    AttemptManager.add_or_update_user_attempt(user_id=user_id, answer_id=answer.id)

    await _log(message, user_id, question.id, answer.key)

    answered_qn = _get_answered_qn(question, answer)

    daily_target_prompt = _get_daily_target_prompt(user_id)

    await message.edit(
        text=str(message.text) + "\n\n" + answered_qn + "\n\n" + daily_target_prompt,
        buttons=Button.inline("Next question", user_id),
    )

    await event.answer()
    raise StopPropagation
