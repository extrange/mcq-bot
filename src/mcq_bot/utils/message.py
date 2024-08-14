from typing import cast

from telethon.custom import Message
from telethon.types import User


def get_user_id(message: Message):
    user_id = message.sender_id
    if not user_id:
        raise Exception(f"No sender in message: {message.text=}")
    return user_id


async def get_user_name(message: Message):
    sender = cast(User, await message.get_sender())
    return sender.username


def extract_command_content(text: str):
    splits = text.split(" ", maxsplit=1)
    if len(splits) < 2:
        return None
    return splits[1]
