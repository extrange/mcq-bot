import uvloop
from sqlalchemy_utils import create_database, database_exists

from mcq_bot.db.connection import get_engine
from mcq_bot.db.schema import Base
from mcq_bot.handlers.register import register_handlers
from mcq_bot.utils.logger import setup_logging

from .client import get_client


async def main():
    setup_logging()
    engine = get_engine()
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine, checkfirst=True)
    client = get_client()

    register_handlers(client)
    await client.start()  # type: ignore
    await client.run_until_disconnected()  # type: ignore


def start():
    uvloop.run(main())


if __name__ == "__main__":
    start()
