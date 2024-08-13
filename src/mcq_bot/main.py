import uvloop
from sqlalchemy_utils import create_database, database_exists
from telethon import TelegramClient

from mcq_bot.db.connection import get_engine
from mcq_bot.db.schema import Base
from mcq_bot.settings import Settings
from mcq_bot.utils.logger import setup_logging


async def main():
    setup_logging()
    engine = get_engine()
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine, checkfirst=True)

    client = TelegramClient(
        Settings.session_file,
        Settings.api_id,
        Settings.api_hash.get_secret_value(),
    )

    await client.start()  # type: ignore
    await client.run_until_disconnected()  # type: ignore


if __name__ == "__main__":
    uvloop.run(main())
