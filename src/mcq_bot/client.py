from functools import cache

from telethon import TelegramClient

from mcq_bot.settings import Settings


@cache
def get_client():
    client = TelegramClient(
        Settings.SESSION_FILE,
        Settings.API_ID,
        Settings.API_HASH.get_secret_value(),
    )
    return client
