import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from src.middleware.router import router
from src.integrations.redis import redis
from src.middleware.throttling import ThrottlingMiddleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from src.api.tg.router import tg_router
from src.integrations.tg_bot import bot
from src.middleware.logger import LogServerMiddleware
from src.on_startup.logger import setup_logger
from src.on_startup.webhook import setup_webhook
from src.utils.background_tasks import tg_background_tasks


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        LogServerMiddleware,
    )
    # CORS Middleware should be the last.
    # See https://github.com/tiangolo/fastapi/issues/1663 .
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],  # type: ignore
        allow_credentials=True,  # type: ignore
        allow_methods=['*'],  # type: ignore
        allow_headers=['*'],  # type: ignore
    )


def setup_routers(app: FastAPI) -> None:
    app.include_router(tg_router)
    app.include_router(router.message.middleware(ThrottlingMiddleware(redis))) # здесь trottling


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print('START APP')
    await setup_webhook(bot)
    setup_logger()

    yield

    logging.info('Stopping')

    # цикл `while` ждет, пока все задачи в `tg_background_tasks` не завершатся
    # цикл нужен, чтобы убедиться, что все фоновые задачи завершены перед остановкой приложения
    while len(tg_background_tasks) > 0:
        logging.info('%s tasks left', len(tg_background_tasks))
        await asyncio.sleep(0)

    logging.info('Stopped')


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)

    url = 'https://web_dev:8000'
    response = requests.get(url)

    print(response.text)

    setup_middleware(app)
    setup_routers(app)

    return app