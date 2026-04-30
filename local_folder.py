"""
    модуль взаимодействия с локальной папкой
"""
import datetime
import os
import pickle
from settings import LOCAL_DIR_PATH, DATA_FILE, app_logger
from typing import Optional, Any


class Folder:
    """
        Класс взаимодействия с локальной папкой
    """
    def __init__(self):
        self.path = LOCAL_DIR_PATH
        self.data_file = DATA_FILE

    def get_files(self) -> set[Optional[Any]]:
        """
        метод для получения названий, дат изменения и размеров всех файлов в локальной папке
        :return:
        result : set[tuple[name: str, modified: datetime, size: str]]
        """
        result = set()
        with os.scandir(self.path) as dir_content:
            for entry in dir_content:
                if entry.is_file():
                    file_name = entry.name
                    file_size = entry.stat().st_size
                    file_mod_date = datetime.datetime.fromtimestamp(entry.stat().st_mtime)
                    # file_mod_date = datetime.datetime.isoformat(file_mod_date)
                    result.add((file_name, file_mod_date, file_size))
        return result

    def update_uploaded_files(self) -> None:
        """
        метод сохраняет данные выгруженных файлов из локальной папки в формате 'pickle'
        :return
        None
        """
        local_files = self.get_files()
        with open(self.data_file, 'wb') as f:
            pickle.dump(local_files, f)

    def get_uploaded_files(self) -> set[Optional[Any]]:
        """
        метод получает данные выгруженных файлов из формата 'pickle'
        :return:
        data : set[tuple[str, datetime.datetime, str]]
        """
        with open(self.data_file, 'rb') as f:
            data = pickle.load(f)
        return data

    def compare_files(self) -> tuple[list[str], list[str]]:
        """
        Метод сравнивает файлы локальной папки и ранее выгруженные файлы,
        если есть изменения, возвращает список удаленных и список измененных файлов
        :return:
        _del : list[str]
        _upload : list[str]
        """
        local_files = self.get_files()
        _del = set()
        _upload = set()
        if not os.path.exists(self.data_file):
            self.update_uploaded_files()
            _upload = {item[0] for item in local_files}
            app_logger.info('Список выгруженных файлов создан')
            return list(_del), list(_upload)
        uploaded_files = self.get_uploaded_files()
        changes = local_files ^ uploaded_files      # local_files.symmetric_difference(uploaded_files)
        for file in changes:
            if file not in local_files:
                _del.add(file[0])
            else:
                _upload.add(file[0])
        _del = _del - _upload
        self.update_uploaded_files()
        if changes:
            app_logger.info(f'Обнаружены изменения в локальной папке...')
        return list(_del), list(_upload)

    def clear_data(self):
        """
        Удаление файла данных синхронизации
        :return:
        """
        if os.path.exists(self.data_file):
            os.remove(self.data_file)


if __name__ == '__main__':
    folder = Folder()
    _del, _upload = folder.compare_files()
    print(f'changed:\n'
          f'for delete - {_del}\n'
          f'for upload - {_upload}\n')
