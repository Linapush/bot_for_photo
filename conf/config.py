from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PHOTO_BACKEND_HOST: str = 'http://web_dev:8000'

    BOT_TOKEN: str
    WEBHOOK_URL: str = ''

    REDIS_HOST: str = 'redis_dev'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0

    LOG_LEVEL: str = ''

    RETRY_COUNT: int = 3
    
    # MAX_DELIVERY_WAIT_TIME: int = 60 * 10

settings = Settings()
