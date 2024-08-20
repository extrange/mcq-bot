import asyncio

import schedule
import uvloop
from sqlalchemy_utils import create_database, database_exists

from mcq_bot.db.connection import get_engine
from mcq_bot.db.schema import Base
from mcq_bot.handlers.register import register_commands, register_handlers
from mcq_bot.utils.logger import setup_logging

from .client import get_client
from .schedule_job import start_schedule
from .settings import Settings


async def main():
    setup_logging()
    engine = get_engine()
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine, checkfirst=True)
    client = get_client()

    register_handlers(client)

    await client.start()  # type: ignore
    await register_commands(client)

    # Start scheduling jobs
    for t in Settings.DAILY_NUDGE_TIMES:
        job = schedule.every().day.at(t.isoformat(), tz=Settings.TZ)
        asyncio.create_task(start_schedule(asyncio.get_running_loop(), job))

    await client.run_until_disconnected()  # type: ignore


def start():
    uvloop.run(main())


if __name__ == "__main__":
    start()
