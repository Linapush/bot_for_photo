from aiogram import F, types
from aiogram.fsm.context import FSMContext

from src.buttons.actions.getter import get_main_keyboard
from src.handlers.user.files.router import files_router
from src.state.file_state import FilesStates
from src.utils.request import do_request
from src.logger import logger
from conf.config import settings

#@files_router.message(FilesStates.waiting_for_day)
@files_router.callback_query(F.data.startswith('download_'))
async def download_photo(message: types.Message | types.CallbackQuery, state: FSMContext):
    logger.info(f"Полученные данные: {message.data}")
   
    if isinstance(message, types.CallbackQuery):
        file_id = message.data.split('_')[1]
        logger.info(f"Получен file_id из callback: {file_id}") 
    else:
        data = await state.get_data()
        logger.info(f"Данные состояния: {data}")
        file_id = data.get('file_id')
        logger.info(f"Получен file_id из состояния: {file_id}")

    if not file_id:
        logger.warning("file_id не найден")
        await message.answer('Не удалось найти информацию о файле для скачивания.',
                             reply_markup=get_main_keyboard(role='user'))
        return
    
    logger.info(f"Начало скачивания файла с ID: {file_id}")
    try:
        logger.info(f"Отправка запроса на скачивание файла с ID: {file_id}")
        headers = {
            'Authorization': f'Bearer {settings.AUTHORIZATION_TOKEN}'
        }
        data = await state.get_data()
        logger.info(f"Данные состояния: {data}")
        try:
            response = await do_request(f"{settings.PHOTO_BACKEND_HOST}/file/download/{file_id}", 'GET', headers=headers)
            logger.info(f"Ответ от API: {response.status}, тело: {await response.text()}")
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса на скачивание файла: {str(e)}, тело: {await response.text()}")
            await message.answer('Не удалось выполнить запрос на скачивание файла.',
                                reply_markup=get_main_keyboard(role='user'))
            logger.error(f"Ошибка при отправке запроса: {str(e)}, тело: {await response.text()}")
            return
        
        logger.info(f"Ответ от API: {response.status}, тело: {await response.text()}")
        if response.status == 200:
            file = await response.read()
            logger.info("Файл успешно скачан")

            file_name = f'downloaded_file_{file_id}.jpg'
            logger.info(f"Полное имя файла: {file_name}")
            

            async with open(file_name.name, 'wb') as f:
                await f.write(file)
            logger.info("Файл успешно сохранен")
            
            await message.answer(
                text='Файл успешно скачан',
                #document=open(file_name, 'rb'),
                document=f,
                reply_markup=get_main_keyboard(role='user') 
            )
            logger.info("Файл успешно отправлен пользователю")
        else:
            await message.answer('Не удалось скачать файл')
            logger.warning("Не удалось скачать файл")
    except Exception as e:
        await message.answer(f'Произошла ошибка при скачивании файла: {str(e)}',
                                reply_markup=get_main_keyboard(role='user'))
        logger.error(f"Ошибка при запросе: {str(e)}")
