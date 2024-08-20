import logging
from functools import cache
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import URL, Engine, create_engine
from sqlalchemy.engine.interfaces import DBAPIConnection

from mcq_bot.settings import Settings

logger = logging.getLogger(__file__)


@cache
def get_engine(db_path: Path | None = None):
    connection_url = URL.create(
        "sqlite",
        database=str(db_path) if db_path else str(Settings.DB_PATH),
    )
    engine = create_engine(connection_url)
    logger.info("Connected to db at %s", connection_url)
    return engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: DBAPIConnection, _):
    """
    Run all sqlite3 connections in WAL mode; reading and writing can be concurrent. See https://www.sqlite.org/wal.html for more info.

    `PoolEvents.connect()`: https://docs.sqlalchemy.org/en/14/core/events.html#sqlalchemy.events.PoolEvents.connect
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
