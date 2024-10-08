from aiohttp import ClientResponseError, FormData
from aiogram import F, types
from aiogram.fsm.context import FSMContext

from conf.config import settings
from src.buttons.actions.getter import UPLOAD_PHOTO, get_main_keyboard
from src.buttons.files.get_download_button import get_download_button
from src.handlers.user.files.router import files_router
from src.logger import logger
from src.state.file_state import update_state_with_file_info
from src.state.waiting_for_photo import UploadPhoto
from src.utils.request import do_request


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ


@files_router.message(F.text == UPLOAD_PHOTO)
async def process_upload_photo(message: types.Message, state: FSMContext):
    logger.info("Загрузить файл в хранилище")
    await state.set_state(UploadPhoto.waiting_for_photo)
    await message.answer("Пожалуйста, выберите файл для загрузки", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Выбрать файл", callback_data="choose_file")],
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_upload")]
        ]
    ))
    logger.info("Переход к выбору файла")


@files_router.callback_query(F.data == "choose_file")
async def handle_choose_file(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Прикрепите файл, пожалуйста.")
    await state.set_state(UploadPhoto.waiting_for_photo)
    logger.info("Выбор файла")


@files_router.callback_query(F.data == "cancel_upload")
async def handle_cancel_upload(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Загрузка отменена.")
    logger.info("Отмена отправки файла")
    await state.clear()
    logger.info("State is clear")


# с do_request и Form data
@files_router.message(UploadPhoto.waiting_for_photo)
async def upload_photo(message: types.Message, state: FSMContext) -> None:
    if message.photo:
        file_id = message.photo[-1].file_id
        logger.info(file_id)
    elif message.document:
        file_id = message.document.file_id
        logger.info(file_id)
    else:
        await message.answer("Пожалуйста, загрузите фото или документ.")
        return

    if file_id:
        file_info = await message.bot.get_file(file_id)
        logger.info(file_info)
        file_name = file_info.file_path.split('/')[-1]
        logger.info(file_name)
        data = await state.get_data()
        logger.info(data)
        file_bytes = await message.bot.download_file(file_info.file_path)
        logger.info(file_bytes)

        form = FormData()
        form.add_field('file', file_bytes, filename=file_name, content_type='multipart/form-data')
        logger.info(form)

        try:
            create_file = await do_request(
                url=f'{settings.PHOTO_BACKEND_HOST}/file/upload',
                data=form
                )
            logger.debug(f"create_file: {create_file}")
            if create_file:
                file_details = create_file
                file_name = file_details.get('file_name')
                file_path = file_details.get('file_path')

                await message.answer(
                    f"Файл '{file_name}' успешно загружен! ({file_path})",
                    reply_markup=get_main_keyboard(role='user')
                )

        except ClientResponseError as e:
            logger.error("Ошибка загрузки файла:", e)
            await message.answer(f"Ошибка загрузки файла: {e}", reply_markup=get_main_keyboard(role='user'))
        except Exception as e:
            logger.error("Произошла ошибка:", e)
            await message.answer(f"Произошла ошибка: {e}", reply_markup=get_main_keyboard(role='user'))
