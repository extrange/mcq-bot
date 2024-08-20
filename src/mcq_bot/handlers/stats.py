from mcq_bot.utils.message import format_stats_message, get_stats, get_user_id
from telethon.custom import Message
from telethon.events import StopPropagation


async def handle_stats(message: Message):
    user_id = get_user_id(message)
    stats = get_stats(user_id)
    stats_message = format_stats_message(stats)

    await message.reply(stats_message)
    raise StopPropagation
