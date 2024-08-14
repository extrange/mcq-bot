import logging

from mcq_bot.senders.send_question import send_question
from mcq_bot.utils.message import get_user_id, get_user_name
from telethon.custom import Message
from telethon.events import StopPropagation

logger = logging.getLogger(__file__)


async def handle_question(message: Message):
    user_id = get_user_id(message)
    user_name = await get_user_name(message)
    logger.info("handle_question called for %s (%s)", user_name, user_id)
    await send_question(user_id)
    raise StopPropagation
