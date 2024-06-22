import os
def check_file_size(file_path: str, max_size: int) -> bool:
       """
       Проверяет размер файла.
       :param file_path: Путь к файлу.
       :param max_size: Максимальный допустимый размер файла в байтах.
       :return: True, если размер файла не превышает max_size, False в противном случае.
       """
       file_size = os.path.getsize(file_path)
       return file_size <= max_size
   
