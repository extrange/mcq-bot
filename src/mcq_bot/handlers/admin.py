from mcq_bot.managers.user import UserManager
from mcq_bot.utils.message import (
    format_stats_message,
    get_attempted_today,
    get_stats,
    get_user_id,
)
from telethon.custom import Message
from telethon.events import StopPropagation


async def handle_admin(message: Message):
    user_id = get_user_id(message)

    msg: list[str] = []

    users = UserManager.get_all_users()
    for user in users:
        stats = get_stats(user.id)
        stats_message = format_stats_message(stats)
        attempted_today = get_attempted_today(user.id)

        msg.append(
            f"{"(You) " if user_id == user.id else ""}"
            f"{stats_message}\n"
            f"Attempted today: {attempted_today}"
        )

    await message.reply("\n\n".join(msg))
    raise StopPropagation
