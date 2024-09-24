import aiohttp

from aiogram import F, types
from aiogram.types import KeyboardButton, BufferedInputFile, URLInputFile
from aiogram.fsm.context import FSMContext
from aiohttp import ClientResponseError

from src.state.file_state import FilesStates
from src.buttons.actions.getter import VIEW_PHOTO, get_main_keyboard
from src.buttons.files.get_download_button import get_download_button
from src.handlers.user.files.router import files_router
from src.logger import logger
from src.utils.request import do_request
from conf.config import settings


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
    logger.info(f'State = waiting_for_month, year = {year}')


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
    logger.info(f'State = waiting_for_day, month = {month}')


@files_router.message(FilesStates.waiting_for_day)
async def process_day(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state == FilesStates.waiting_for_day.state: 
        day = int(message.text)
        logger.info(f"День {day}")
        state_data = await state.get_data()
        logger.info(f"Год, месяц из стейт {state_data}")
        year = state_data.get('year')
        logger.info(f"Год {year}")
        month = state_data.get('month')
        logger.info(f"Месяц {month}")
        logger.info(f"Пользователь {user_id} выбрал дату: {year}-{month}-{day}")

        try: # api_response — словарь, нужно проверить наличие ключа 'data' в словаре
            api_response = await do_request(
                f'{settings.PHOTO_BACKEND_HOST}/file/file/?year={year}&month={month}&day={day}',
                method='GET'
            )
            logger.info(f"Данные из do_request: {api_response}")
        except ClientResponseError as e:
            if "Not Found" in e.message:
                await message.answer('Файлы не найдены для указанных параметров.')
                logger.info('File not found')
                return
            else:
                await message.answer('Ваш код неверный')
                logger.info('Code Error')
            return
        
        if isinstance(api_response, list) and api_response:
            logger.info("Получен непустой список файлов.")
            files = api_response
            for file_data in files:
                logger.info(f"Информация о файле: {file_data}")
                file_info = file_data

                if file_info:
                    file_name = file_info.get('file_name')
                    file_id = file_info.get('id')
                    file_type = file_info.get('file_type')
                    download_url = file_info.get('download_url')

                    if not download_url:
                        logger.error("Download URL отсутствует.")
                        await message.answer("Ошибка: ссылка для скачивания файла отсутствует.")
                        continue

                    try:
                        headers = {
                            'Authorization': f'Bearer {settings.AUTHORIZATION_TOKEN}'
                        }
                        async with aiohttp.ClientSession() as session:
                            async with session.get(download_url, headers=headers) as resp:
                                if resp.status == 200:
                                    file_bytes = await resp.read()
                                else:
                                    logger.error(f"Ошибка при запросе файла: статус {resp.status}")
                                    await message.answer("Ошибка при получении файла. Попробуйте позже.")
                                    continue
                    except Exception as e:
                        logger.error(f"Ошибка при запросе файла: {e}")
                        await message.answer("Ошибка при получении файла. Попробуйте позже.")
                        continue

                    file_input = BufferedInputFile(file_bytes, filename=file_name)

                    try:
                        if file_type.startswith('image/'):
                            await message.answer_photo(
                                photo=file_input,
                                caption=f"File ID: {file_id}",
                                reply_markup=get_download_button(file_id),
                            )
                        else:
                            await message.answer_document(
                                document=file_input,
                                caption=f"File ID: {file_id}",
                                reply_markup=get_download_button(file_id),
                            )
                        logger.info(f"Файл успешно передан: file_id={file_id}, file_name={file_name}")

                    except Exception as e:
                        logger.error(f"Ошибка при отправке файла: {e}")
                        await message.answer("Ошибка при отправке файла. Попробуйте позже.")
                else:
                    logger.warning("Отсутствует информация о файле.")
                    await message.answer("Ошибка: данные о файле отсутствуют.")
        else:
            logger.warning("Список файлов пуст.")
            await message.answer('Файлы не найдены для указанных параметров.')

            
            # if len(files) > 0:
            #     for file_info in files:
            #         logger.info(f'Инф. в файле{file_info}')
            #         file_name = file_info.get('file_name')
            #         file_id = file_info.get('id')

            #         if file_name and file_id:
            #             logger.info(f"Имя файла: {file_name}")
            #             logger.info(f"ID Файла: {file_id}")
            #             logger.info(f"ID Файла: {type(file_id)}")

            #             file_id_str = str(file_id)
            #             logger.info(f"Преобразованный ID Файла: {file_id_str}")
            #             logger.info(f"Тип преобразованного ID Файла: {type(file_id_str)}")

            #             file_url = f"{settings.PHOTO_BACKEND_HOST}/file/{file_id_str}" 
            #             logger.info(f"Сформированный URL: {file_url}")

            #             if file_url.startswith(('http://', 'https://')) and file_url:
            #                 logger.info(f"Отправка фото с URL: {file_url} и ID файла: {file_id}")  

            #                 response = requests.get(file_url)
            #                 if response.status_code == 200:
            #                     content = response.content

            #                     photo_input_file = InputFile(BytesIO(content), filename=file_name) 
            #                     logger.info(f"Объект файла успешно создан: {photo_input_file}")   

            #                     await message.answer_photo(
            #                         photo=photo_input_file,
            #                         #photo=file_url,
            #                         caption=f"File ID: {file_id}",
            #                         reply_markup=get_download_button(file_id),
            #                     )
            #                     logger.info(f"Файл успешно передан: file_id={file_id}, file_name={file_url}")
            #                 else:
            #                     logger.error(f"Ошибка загрузки файла: получен статус код {response.status_code} для URL: {file_url}")

            #                     if response.status_code == 404:
            #                         await message.answer("Ошибка: файл не найден.")
            #                     elif response.status_code == 500:
            #                         await message.answer("Ошибка: внутреняя ошибка сервера. Попробуйте позже.")
            #                     else:
            #                         await message.answer("Ошибка: не удалось загрузить файл. Пожалуйста, проверьте доступность файла.")
            #             else:
            #                 logger.warning(f"Некорректный URL: {file_url}")
            #                 await message.answer("Ошибка: некорректный URL для файла.")

            #             # обновляем состояние для каждого файла, если это необходимо
            #             await state.update_data(file_id=file_id)
            #         else:
            #             logger.warning("URL или ID файла отсутствует.")
            #             await message.answer("Ошибка: имя файла или ID отсутствует.")
            #     return 
            # else:
            #     logger.warning("Список файлов пуст.")
            #     await message.answer('Ошибка: файлы не найдены для указанных параметров.')


#############################################################
# старый вариант
# @files_router.message(F.text & FilesStates.waiting_for_day)
# @files_router.message(F.text)
# @files_router.message(FilesStates.waiting_for_day)
# async def process_day(message: types.Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state == FilesStates.waiting_for_day.state:
#         day = int(message.text)
#         data = await state.get_data()
#         year = data.get('year')
#         month = data.get('month')
#         user_id = message.from_user.id

#         logger.info(f"Пользователь {user_id} выбрал дату: {year}-{month}-{day}")

#         try:
#             file_info = await do_request(
#                 f'{settings.PHOTO_BACKEND_HOST}/file/{year}/{month}/{day}',
#                 json={'user_id': user_id}
#             )
#             logger.info(f"Запрос на сервер отправлен: {file_info}")

#             if file_info:
#                 file_url = file_info['file_url']
#                 file_id = file_info['file_id']
#                 input_file = InputFile(file_url)
#                 await message.answer_photo(
#                     photo=input_file,
#                     caption=f"File ID: {file_id}",
#                     reply_markup=get_download_button(file_id),
#                 )
#                 logger.info('Файлы переданы')
#                 return

#             await message.answer('Файлы не найдены для указанных параметров.')
#             logger.info('Файлы не найдены')
#             return

#         except ClientResponseError as e:
#             if e.status == 404:
#                 await message.answer(
#                     'Файлы не найдены для указанных параметров.',
#                     reply_markup=get_main_keyboard(role='user'))
#                 logger.info('Файлы не найдены')
#                 return
#             else:
#                 await message.answer('Произошла ошибка.')
#                 logger.error(f'Error getting files: {e}')
#                 return
        
###########
# file_url = f"http://localhost:8002/file/file/{quote(file_id)}"
# bot  | quote_from_bytes() expected bytes 

# file_url = f"http://localhost:8002/file/file/{file_id}"
# file_url = f"http://localhost:8002/file/{str(file_id)}"
# bot  | Telegram server says - Bad Request: wrong remote file identifier specified: Wrong character in the string
