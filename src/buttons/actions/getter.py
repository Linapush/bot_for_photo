from typing import Callable, ParamSpec

from aiogram import types


UPLOAD_PHOTO = 'Загрузить фото в хранилище'
VIEW_PHOTO = 'Посмотреть фото'
DOWNLOAD_PHOTO = 'Скачать выбранное фото'


P = ParamSpec('P')


def get_main_keyboard(role: str, **kwargs) -> types.ReplyKeyboardMarkup:
    return role_to_keyboard_getter[role](**kwargs)


def _get_keyboard_user(*kwargs) -> types.ReplyKeyboardMarkup:
    kb = [
        [types.KeyboardButton(text=UPLOAD_PHOTO, callback_data="choose_file")],
        [types.KeyboardButton(text=VIEW_PHOTO)],
        # [types.KeyboardButton(text=SELECT_PHOTO)],
        # [types.KeyboardButton(text=DOWNLOAD_PHOTO)],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

role_to_keyboard_getter: dict[str, Callable[..., types.ReplyKeyboardMarkup]] = {
    'user': _get_keyboard_user,
}
