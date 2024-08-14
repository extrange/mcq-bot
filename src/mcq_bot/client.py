from functools import cache

from telethon import TelegramClient

from mcq_bot.settings import Settings


@cache
def get_client():
    client = TelegramClient(
        Settings.session_file,
        Settings.api_id,
        Settings.api_hash.get_secret_value(),
    )
    return client
