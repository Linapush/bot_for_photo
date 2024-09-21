from io import BytesIO

from aiogram import types
from aiogram.types import InputFile

from src.logger import logger


async def send_file_to_user(message: types.Message, file_url: str, file_name: str):
    """Отправляет файл пользователю в Telegram."""
    response = requests.get(file_url)
    logger.info(f"Запрос: {response.status_code}, {response.reason}")
    if response.status_code == 200:
        content = response.content
        logger.info(f"Содержимое запроса: {content}")

        photo_input_file = InputFile(BytesIO(content), filename=file_name)
        logger.info(f"Объект файла успешно создан: {photo_input_file}")   

        await message.answer_photo(
            photo=photo_input_file,
            caption=f"File ID: {file_id_str}",
            reply_markup=get_download_button(file_id_str),
        )
        logger.info(f"Файл успешно передан: file_id={file_id}, file_name={file_url}")
    else:
        response.raise_for_status()
        logger.error(f"Ошибка загрузки файла: получен статус код {response.status_code} для URL: {file_url}")

        if response.status_code == 404:
            await message.answer("Ошибка: файл не найден.")
        elif response.status_code == 500:
            await message.answer("Ошибка: внутреняя ошибка сервера. Попробуйте позже.")
        else:
            await message.answer("Ошибка: не удалось загрузить файл. Пожалуйста, проверьте доступность файла.")
