from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiohttp import ClientResponseError
from src import state
from src.state.file_state import FilesStates
from src.buttons.actions.getter import VIEW_PHOTO, get_main_keyboard
from src.buttons.files.get_download_button import get_download_button
from src.handlers.user.files.router import files_router
from src.logger import logger
# from src.template.render import render
from src.utils.request import do_request
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from conf.config import settings

# FSMContext (Finite State Machine) для отслеживания состояний пользователя
BOT_TOKEN = settings.BOT_TOKEN


YEAR_KEYBOARD = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
year_buttons = []
for year in range(2000, 2030):
    year_buttons.append([KeyboardButton(text=str(year))])
YEAR_KEYBOARD.keyboard = year_buttons


MONTH_KEYBOARD = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
month_buttons = []
for month in range(1, 13):
    month_buttons.append([KeyboardButton(text=str(month))])
MONTH_KEYBOARD.keyboard = month_buttons


DAY_KEYBOARD = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
day_buttons = []
for day in range(1, 32):
    day_buttons.append([KeyboardButton(text=str(day))])
DAY_KEYBOARD.keyboard = day_buttons


# обработчик, состояние VIEW_PHOTO
@files_router.message(F.text == VIEW_PHOTO)
async def view_photo(message: types.Message, state: FSMContext) -> None:
    await message.answer("Выберите год:", reply_markup=YEAR_KEYBOARD)
    # await FilesStates.waiting_for_year.set()
    await state.set_state(FilesStates.waiting_for_year)
    logger.info('State = waiting_for_year')


# @files_router.message(F.text & FilesStates.waiting_for_year)
# @files_router.message(F.text)
@files_router.message(FilesStates.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext) -> None:
    # current_state = await state.get_state()  # Await the coroutine
    # if current_state == FilesStates.waiting_for_year.state: 
        year = int(message.text)
        await state.update_data(year=year)
        await message.answer("Выберите месяц:", reply_markup=MONTH_KEYBOARD)
        # await FilesStates.waiting_for_month.set()
        await state.set_state(FilesStates.waiting_for_month)
        logger.info('State = waiting_for_month')


# @files_router.message(F.text & FilesStates.waiting_for_month)
# @files_router.message(F.text)
@files_router.message(FilesStates.waiting_for_month)
async def process_month(message: types.Message, state: FSMContext) -> None:
    # current_state = await state.get_state()  # Await the coroutine
    # if current_state == FilesStates.waiting_for_month.state:    
        month = int(message.text)
        await state.update_data(month=month)
        await message.answer("Выберите день:", reply_markup=DAY_KEYBOARD)
        # await FilesStates.waiting_for_day.set()
        await state.set_state(FilesStates.waiting_for_day)
        logger.info('State = waiting_for_day')


# @files_router.message(F.text & FilesStates.waiting_for_day)
# @files_router.message(F.text)
@files_router.message(FilesStates.waiting_for_day)
async def process_day(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()  # Await the coroutine
    if current_state == FilesStates.waiting_for_day.state: 
        day = int(message.text)
        data = await state.get_data()
        year = data.get('year')
        month = data.get('month')

        try:
            data = await do_request(
                f'{settings.PHOTO_BACKEND_HOST}/file?year={year}&month={month}&day={day}',
                headers={'Authorization': f'Bearer {BOT_TOKEN}'},
            )
        except ClientResponseError as e:
            if "Not Found" in e.message:
                await message.answer('Файлы не найдены для указанных параметров.')
                logger.info('File not found')
                return
            else:
                await message.answer('Ваш код неверный')
                logger.info('Code Error')
            return
        if files := data['data']:
            file_info = files[0]  # берем первый файл из списка, который подходит по параметрам

            await message.answer_photo(
                photo=file_info['file_url'],
                caption=f"File ID: {file_info['file_id']}",
                reply_markup=get_download_button(file_info['file_id']),)  # передаем file_id для кнопки "Скачать"
            logger.info('File transferred')
        
            await state.update_data(file_id=file_info['file_id'])  # сохраняем file_id в состоянии
            return
        await message.answer('Файлы не найдены для указанных параметров.')
        logger.info('File not found')
