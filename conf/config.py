from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PHOTO_BACKEND_HOST: str = 'http://web_dev:8002'

    BOT_TOKEN: str
    WEBHOOK_URL: str = ''

    REDIS_HOST: str = 'redis_dev'
    REDIS_PORT: int = 6378
    REDIS_PASSWORD: str
    REDIS_DB: int = 0

    LOG_LEVEL: str = ''

    RETRY_COUNT: int = 3


settings = Settings()
