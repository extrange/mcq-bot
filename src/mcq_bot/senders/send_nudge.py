from mcq_bot.client import get_client
from telethon import Button


async def send_nudge(user_id: int):
    client = get_client()
    text = "Time to do some questions!"
    await client.send_message(
        user_id, text, buttons=Button.inline("I'm ready!", data=user_id)
    )
