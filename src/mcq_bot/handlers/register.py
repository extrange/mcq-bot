import logging

from telethon import TelegramClient, events

from .exam import handle_exam_date
from .question import handle_question
from .question_callback import handle_question_callback
from .start import handle_start

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
    client.add_event_handler(handle_question_callback, events.CallbackQuery())
