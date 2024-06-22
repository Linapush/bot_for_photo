import random
import string
import time
from aiogram import types
from src.utils.request import do_request
from conf.config import settings
from aiohttp.client_exceptions import ClientResponseError
from src.logger import logger


# async def get_unique_code() -> str:
#     code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#     return code

async def create_unique_code() -> str:
    current_milliseconds = int(round(time.time() * 1000))
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code = f'CODE-{current_milliseconds}-{random_suffix}'
    return code


async def get_or_create_unique_code(user_id: int) -> str:
    existing_code = await get_existing_code(user_id)
    if existing_code == '':
        unique_code = await  create_unique_code()
        await save_code_to_database(user_id, unique_code)
        return unique_code
    else:
        return existing_code


# извлечение кода пользователя
async def get_existing_code(user_id: int) -> str:
    try:
        data = await do_request(
            f'{settings.PHOTO_BACKEND_HOST}/auth/get_code',
            json={
                'username': user_id,
            },
        )
        logger.info("Выбран существующий код")
        return data['code']  
    except ClientResponseError:
        logger.error('Code error')
        return ''
    
# создание кода для пользователя
async def save_code_to_database(user_id: int, code: str):
    try:
        await do_request(
            f'{settings.PHOTO_BACKEND_HOST}/auth/save_code',
            json={
                'username': user_id,
                'code': code,
            },
        )
        logger.info("Код сохранен успешно")
    except ClientResponseError:
        logger.error("Ошибка в сохранении кода")

