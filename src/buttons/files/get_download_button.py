from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# get_download_button для process_day

def get_download_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Скачать фото на устройство',
            callback_data='download',
        ),
    )
    return builder.as_markup()
 
# def get_download_button(file_id: str) -> types.ReplyKeyboardMarkup:
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(types.KeyboardButton(text=DOWNLOAD_PHOTO))
#     return keyboard
