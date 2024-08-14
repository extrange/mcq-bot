from datetime import time
from pathlib import Path

from pydantic import IPvAnyAddress, SecretStr
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    # Telegram related
    api_id: int
    api_hash: SecretStr
    session_file: Path
    dc: IPvAnyAddress
    db: Path
    bot_token: SecretStr
    daily_nudge_time: time = time(7, 0)

    openai_api_key: SecretStr
    notify_chat_id: int


Settings = _Settings.model_validate({})
