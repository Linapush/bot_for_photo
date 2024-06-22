import asyncio
import logging
from asyncio import Task
from typing import Any

from aiogram import Bot, Dispatcher, types
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from src.api.tg.router import tg_router
from src.integrations.tg_bot import get_dispatcher, get_tg_bot
from src.utils.background_tasks import tg_background_tasks

# роутер, обрабатывает запросы, связанные с ботом
# получает обновления (updates) от Telegram API и обработки их через aiogram фреймворк
# Request - HTTP-запрос, полученный от Telegram (post, /th, тело: JSON)
# Dispatcher - параметр который получает объект Dispatcher, 
@tg_router.post('/tg')
async def tg_api(
    request: Request,
    dp: Dispatcher = Depends(get_dispatcher),
    bot: Bot = Depends(get_tg_bot),
) -> ORJSONResponse:                # ф-ция должна вернуть объект ORJSONResponse
    logging.info('tg_api')
    data = await request.json()     # асинхронное извлечение данных из тела входящего HTTP-запроса
    update = types.Update(**data)   # обновления от Telegram API 
    # создание асинхронной задачи и добавление в список задач
    task: Task[Any] = asyncio.create_task(dp.feed_webhook_update(bot, update))
    tg_background_tasks.add(task)

    logging.info(len(tg_background_tasks))

    task.add_done_callback(tg_background_tasks.discard)

    logging.info(data)

    return ORJSONResponse({'success': True})
