from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiohttp import ClientResponseError, ClientSession
# from conf.config import BOT_TOKEN
from src.buttons.actions.getter import DOWNLOAD_PHOTO
from src.buttons.files.get_download_button import get_download_button
from src.handlers.user.files.router import files_router
from src.utils.request import do_request
from conf.config import settings


files_router.message(F.text == DOWNLOAD_PHOTO)
async def download_photo(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    file_id = data.get('file_id')
    
    if file_id:
        try:
            response = await do_request('GET', f'/download/{file_id}', headers={'Authorization': f'Bearer {settings.BOT_TOKEN}'})
            if response.status == 200:
                file = await response.read()
                file_name = f"file_{file_id}.jpg"
                with open(file_name, 'wb') as f:
                    f.write(file)
                await message.answer_document(document=open(file_name, 'rb'), caption='Файл успешно скачан')
            else:
                await message.answer('Не удалось скачать файл')
        except Exception as e:
            await message.answer(f'Произошла ошибка при скачивании файла: {str(e)}')
    else:
        await message.answer('Не удалось найти информацию о файле для скачивания.')






# старый вариант, без сохраненного file_data из view_photo.py
# @files_router.message(F.text == DOWNLOAD_PHOTO)
# async def download_photo(message: types.Message, state: FSMContext) -> None:
#     data = await state.get_data() # ожидаем стейт get_data
#     file_id = data.get('file_id') 

#     try:
#         response = await do_request('GET', f'/download/{file_id}', headers={'Authorization': f'Bearer {settings.BOT_TOKEN}'})
#         if response.status == 200:
#             file = await response.read()
#             file_name = f"file_{file_id}.jpg" 
#             with open(file_name, 'wb') as f:
#                 f.write(file)
#             await message.answer_document(document=open(file_name, 'rb'), caption='Файл успешно скачан')
#         else:
#             await message.answer('Не удалось скачать файл')
#     except Exception as e:
#         await message.answer(f'Произошла ошибка при скачивании файла: {str(e)}')


# async def upload_photo(message: types.Message):
#     file_id = message.photo[-1].file_id
#     async with ClientSession() as session:
#         async with session.get(f'http://your-api-url/download/{file_id}') as resp:
#             if resp.status == 200:
#                 with open(f'{file_id}.jpg', 'wb') as file:
#                     file.write(await resp.content.read())
#                 await message.answer_photo(types.InputFile(f'{file_id}.jpg'))
#             else:
#                 await message.answer("Не удалось загрузить фото")

