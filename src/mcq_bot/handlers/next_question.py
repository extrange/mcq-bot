from typing import cast

from mcq_bot.senders.send_question import send_question
from telethon import events
from telethon.custom import Message
from telethon.events import StopPropagation


async def handle_next_question_callback(event: events.CallbackQuery.Event):
    await send_question(int(event.data))
    message = cast(Message, await event.get_message())
    await message.edit(buttons=None)
    await event.answer()
    raise StopPropagation
