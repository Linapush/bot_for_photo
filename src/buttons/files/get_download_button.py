from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# get_download_button для process_day

def get_download_button(file_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Скачать фото на устройство',
            callback_data=f'download_{file_id}',
        ),
    )
    return builder.as_markup()
 