import logging

from mcq_bot.senders.sender_types import is_answer_callback
from telethon import TelegramClient, events, functions, types

from .exam import handle_exam_date
from .next_question import handle_next_question_callback
from .question import handle_question
from .question_callback import handle_question_callback
from .start import handle_start
from .stats import handle_stats

logger = logging.getLogger(__file__)


def register_handlers(client: TelegramClient):
    """
    Registered handlers will be called in order, so add the most specific ones first.

    Raise a StopPropagation if no further handlers should handle the message.
    """
    # client.add_event_handler(_handle_cancel, events.CallbackQuery(data="cancel"))
    # client.add_event_handler(_handle_msg, events.NewMessage(incoming=True))
    client.add_event_handler(
        handle_start, events.NewMessage(incoming=True, pattern="/start")
    )
    client.add_event_handler(
        handle_exam_date, events.NewMessage(incoming=True, pattern="/exam")
    )
    client.add_event_handler(
        handle_question, events.NewMessage(incoming=True, pattern="/question")
    )
    client.add_event_handler(
        handle_stats, events.NewMessage(incoming=True, pattern="/stats")
    )
    client.add_event_handler(
        handle_next_question_callback, events.CallbackQuery(pattern=rb"\d+")
    )
    client.add_event_handler(
        handle_question_callback, events.CallbackQuery(data=is_answer_callback)
    )
    logger.info("Registered handlers successfully.")


async def register_commands(client: TelegramClient):
    result = await client(
        functions.bots.SetBotCommandsRequest(
            scope=types.BotCommandScopeDefault(),
            lang_code="en",
            commands=[
                types.BotCommand(command="exam", description="Set your exam date"),
                types.BotCommand(
                    command="question", description="Start doing questions"
                ),
                types.BotCommand(command="stats", description="Show your stats"),
            ],
        )
    )
    logger.info("Registering commands...%s", "successful" if result else "failed")
