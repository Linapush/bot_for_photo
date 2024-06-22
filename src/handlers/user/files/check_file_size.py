from aiogram import types

def check_file_size(file: types.File, max_file_size: int) -> bool:
    return file.file_size <= max_file_size

