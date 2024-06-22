import asyncio
from src.state.login import LoginState
from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

from src.handlers.main.router import main_router
from src.logger import logger
from src.handlers.main.save_and_create_code import get_or_create_unique_code


@main_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info('Start cmd')
    logger.info('User: %s, %s start bot', user_id, username)


    welcome_message = (
        'Приветствую! Это бот для хранения фотографий.\n\n'
        'С помощью бота Вы можете загрузить фото в хранилище, просматривать их и загружать на устройство.\n\n'
        'Для начала работы введите уникальный код 👇'
    )

    unique_code = await get_or_create_unique_code(user_id)

    await message.answer(welcome_message)
    await asyncio.sleep(0.3)
    await message.answer('Если у вас уже есть код, введите его.\n'
                        f'Или воспользуйтесь этим: {unique_code}')
    await asyncio.sleep(0.3)
    await state.set_state(LoginState.enter_code)