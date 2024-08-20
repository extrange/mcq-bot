from datetime import time
from pathlib import Path

from pydantic import IPvAnyAddress, SecretStr
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    # Telegram related
    API_ID: int
    API_HASH: SecretStr
    SESSION_FILE: Path
    TELEGRAM_DC: IPvAnyAddress
    DB_PATH: Path
    BOT_TOKEN: SecretStr

    # In SGT
    # Example: ["0700","1100"]
    DAILY_NUDGE_TIMES: list[time]

    OPENAI_API_KEY: SecretStr
    NOTIFY_CHAT_ID: int
    TZ: str


Settings = _Settings.model_validate({})
