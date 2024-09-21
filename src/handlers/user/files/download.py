import io

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from src.buttons.actions.getter import get_main_keyboard
from src.handlers.user.files.router import files_router
from src.state.file_state import FilesStates
from src.utils.request import do_request


@files_router.message(FilesStates.waiting_for_day)
@files_router.callback_query(F.data.startswith('download_'))
async def download_photo(message: types.Message | types.CallbackQuery, state: FSMContext):

    if isinstance(message, types.CallbackQuery):
        file_id = message.data.split('_')[1]
    else:
        data = await state.get_data()
        file_id = data.get('file_id')

    if file_id:
        try:
            data = await state.get_data()
            response = await do_request(
                'GET',
                f'/download/{file_id}',
            )
            if response.status == 200:
                file = await response.read()
                file_name = io.BytesIO()
                with open(file_name, 'wb') as f:
                    f.write(file)
                    f.seek(0)
                await message.answer(
                    text='Файл успешно скачан',
                    document=open(file_name, 'rb'),
                    reply_markup=get_main_keyboard(role='user') 
                )
            else:
                await message.answer('Не удалось скачать файл')
        except Exception as e:
            await message.answer(f'Произошла ошибка при скачивании файла: {str(e)}',
                                 reply_markup=get_main_keyboard(role='user'))
    else:
        await message.answer('Не удалось найти информацию о файле для скачивания.',
                             reply_markup=get_main_keyboard(role='user'))
