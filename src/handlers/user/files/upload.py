from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiohttp import ClientResponseError, FormData
from src.logger import logger
from src.buttons.actions.getter import UPLOAD_PHOTO
from src.handlers.user.files.router import files_router
from src.utils.request import do_request
from fastapi import UploadFile
from src.state.waiting_for_photo import UploadPhoto
from src.handlers.user.files.check_file_size import check_file_size
from src.buttons.actions.getter import get_main_keyboard


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
    

@files_router.message(UploadPhoto.waiting_for_photo)
async def upload_photo(message: types.Message, state: FSMContext):
    logger.info("Пользователь отправляет файл")

    if message.photo and len(message.photo) > 0:
        file_id = message.photo[-1].file_id
        file_name = message.photo[-1].file_name 
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name 
    else:
        await message.answer("Пожалуйста, отправьте фотографию или файл.")
        logger.info("Пользователь не отправил фото или файл.")
        return

    file = await message.bot.get_file(file_id)
    file_bytes = await file.download(dest='tmp_file')

    if not check_file_size(file, MAX_FILE_SIZE):
        await message.answer(f"Размер файла слишком большой. Максимальный размер: {MAX_FILE_SIZE} байт.")
        logger.info("Слишком большой файл")
        return

    await message.answer("Загрузка файла...")
    logger.info("Загрузка файла...")

    try:
        data = FormData()
        data.add_field('file', file_bytes, filename=file_name)
        # file_name = file.file_path.split('/')[-1]
        # upload_file = UploadFile(file=file, filename=file_name)
        logger.info("Отправляем файл на сервер:", file_name)
        # response = await do_request('POST', '/upload_file', file=upload_file)
        response = await do_request('POST', '/upload_file', data=data)
        logger.info("Получен ответ от сервера:", response)
        await message.answer("Файл успешно загружен в MINIO!", reply_markup=get_main_keyboard(role='user'))
        logger.info("Файл успешно загружен в MINIO")

    except ClientResponseError as e:
        logger.error("Ошибка загрузки файла:", e)
        await message.answer(f"Ошибка загрузки файла: {e} во время выполнения запроса: {response}")
    except Exception as e:
        logger.error("Произошла ошибка:", e)
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        await state.clear()
        logger.info("State is clear")