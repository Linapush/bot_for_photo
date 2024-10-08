from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from src.integrations.redis import redis
from src.middleware.auth import AuthMiddleware
from src.middleware.logger import LogMessageMiddleware
from src.middleware.throttling import ThrottlingMiddleware

from src.handlers.login.router import login_router
from src.handlers.main.router import main_router
from src.handlers.user.router import user_router
from src.handlers.user.files.router import files_router


def setup_dispatcher(bot: Bot) -> Dispatcher:
    storage = RedisStorage(redis)
    dp = Dispatcher(storage=storage, bot=bot)

    dp.message.middleware(ThrottlingMiddleware(redis)) # здесь trottling

    dp.include_routers(main_router)
    dp.include_routers(login_router)

    dp.include_routers(user_router)
    dp.include_routers(files_router)

    dp.message.middleware(LogMessageMiddleware())
    dp.callback_query.middleware(LogMessageMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    return dp
