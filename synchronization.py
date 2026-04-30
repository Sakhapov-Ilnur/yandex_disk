"""
    Модуль синхронизации локальной и удалённой папок
"""
import time
from settings import app_logger, LOCAL_DIR_PATH, REMOTE_DIR_PATH, DATA_FILE, SYNCHRONIZATION_PERIOD, LOG_FILE
from yandex_API import API
from local_folder import Folder
import os


class Synchronization:
    """
        Удаление папки на Яндекс.Диске
        Класс синхронизации локальной папки и папки на Яндекс.Диске
     """
    def __init__(self):
        self.folder = Folder()
        self.yandex_disk = API()
        self.remote_files = []
        self.local_files = []

    def check_resources(self) -> None:
        """
        Начальная сверка ресурсов
        :return:
        """
        if self.yandex_disk.check_directory()[0] != 200:
            app_logger.warning(f'Папка "{REMOTE_DIR_PATH}" не найдена, попытаемся создать...')
            status_code, response = self.yandex_disk.create_directory()
            if status_code in (200, 201):
                app_logger.info(f'Папка "{REMOTE_DIR_PATH}" создана')
            else:
                app_logger.error(f'Работа не возможна!!!\n\t -> {status_code, response}')
                exit(-1)
        else:
            app_logger.info(f'Папка "{REMOTE_DIR_PATH}" на "яндекс.диске" доступна')
            status_code, self.remote_files = self.yandex_disk.check_files()
            app_logger.info(f'Количество файлов на "яндекс.диске": {len(self.remote_files)}')

        if not os.path.exists(DATA_FILE):
            app_logger.warning(f'Локальная папка "{LOCAL_DIR_PATH}" не синхронизирована!')

            self.local_files = [item[0] for item in self.folder.get_files()]
            app_logger.info(f'Количество файлов в локальной папке {LOCAL_DIR_PATH}: {len(self.local_files)}')
            extra_files = set(self.remote_files) - set(self.local_files)
            if extra_files:
                self.yandex_disk.delete_files(list(extra_files))
                app_logger.info(f'Удалено лишних файлов: {len(extra_files)}')

            self.yandex_disk.upload_files(self.local_files)
            app_logger.info(f'Выгружено файлов: {len(self.local_files)}')
            self.folder.update_uploaded_files()
            app_logger.info(f'Папка {LOCAL_DIR_PATH} синхронизирована!\n')
            self.remote_files = self.yandex_disk.check_files()[1]
        else:
            self.__exec()
            app_logger.info(f'Локальная папка "{LOCAL_DIR_PATH}" синхронизирована!')

    def __exec(self):
        """
        Синхронизация файлов локальной папки и папки на Яндекс.Диске
        :return:
        """
        _del, _upload = self.folder.compare_files()
        if _del:
            self.yandex_disk.delete_files(_del)
            app_logger.info(f'Удалено лишних файлов: {len(_del)}')
        if _upload:
            self.yandex_disk.upload_files(_upload)
            app_logger.info(f'Выгружено измененных  файлов: {len(_upload)}')
        local_files = [item[0] for item in self.folder.get_files()]
        self.local_files = local_files
        self.remote_files = self.yandex_disk.check_files()[1]
        extra_files = set(self.remote_files) - set(self.local_files)
        if extra_files:
            self.yandex_disk.delete_files(list(extra_files))
        missing_files = set(self.local_files) - set(self.remote_files)
        if missing_files:
            self.yandex_disk.upload_files(list(missing_files))
        local_files = [item[0] for item in self.folder.get_files()]
        self.local_files = local_files
        self.remote_files = self.yandex_disk.check_files()[1]

    def start(self, period=int(SYNCHRONIZATION_PERIOD)):
        """
        Запуск периодической синхронизации файлов локальной папки и папки на Яндекс.Диске
        бесконечный цикл
        :param period: int
        :return:
        """
        app_logger.info(f'Начали контроль изменения папки "{LOCAL_DIR_PATH}", период синхронизации: {period} сек.')
        while True:
            self.__exec()
            time.sleep(period)

    def clear_data(self):
        """
        Очистка данных синронизации, удаление папки на Яндекс.Диске
        :return:
        """
        self.folder.clear_data()
        self.yandex_disk.delete_remote_folder()
        if os.path.exists(LOG_FILE):
            app_logger.remove()
            os.remove(LOG_FILE)
        exit()


if __name__ == '__main__':
    synchronization = Synchronization()
    # synchronization.check_resources()
    # synchronization.clear_data()
