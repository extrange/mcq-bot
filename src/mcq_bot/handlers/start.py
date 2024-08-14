from telethon.custom import Message
from telethon.events import StopPropagation


async def handle_start(message: Message):
    await message.reply(
        """
        Hi! Before we begin, please tell me your exam date with `/exam your-exam-date`.

        For example: `/exam 22 Oct 2024`
        """
    )
    raise StopPropagation
