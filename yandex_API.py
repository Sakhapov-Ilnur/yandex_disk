"""
    Модуль взаимодействия с API yandex.диска
"""
import os.path
import time
import requests
from settings import HOST_API, API_KEY, LOCAL_DIR_PATH, REMOTE_DIR_PATH, app_logger
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


class API:
    """
        Класс взаимодействия с папкой на Яндекс.Диске
    """
    ERRORS = {
        400: 'Некорректные данные.',
        401: 'Не авторизован.',
        403: 'API недоступно.Ваши файлы занимают больше места, чем у вас есть.Удалите лишнее или увеличьте объём Диска.',
        404: 'Не удалось найти запрошенный ресурс.',
        406: 'Ресурс не может быть представлен в запрошенном формате.',
        409: 'Ресурс по указанному пути уже существует.',
        413: 'Загрузка файла недоступна, файл слишком большой(UPLOAD_FILE_SIZE_LIMIT_EXCEEDED).',
        423: 'Загрузка файлов недоступна, можно только просматривать и скачивать.',
        429: 'Слишком много запросов.',
        503: 'Сервис временно недоступен.',
        507: 'Недостаточно свободного места.'
    }

    def __init__(self):
        self.URL = HOST_API
        self.API_KEY = API_KEY
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.API_KEY}'}

    def check_directory(self) -> tuple[int, dict[str, str]]:
        """
        Метаинформация о папке на Яндекс.Диске
        :return:
        status_code: str
        result: dict[str, str]
        """
        status_code, result = None, None
        try:
            response = requests.get(f'{self.URL}?path={REMOTE_DIR_PATH}', headers=self.headers, timeout=5)
            status_code = response.status_code
            result = response.json()
        except Exception as exc:
            app_logger.error(exc)

        return status_code, result

    def get_info(self) -> tuple[int, list[str]]:
        """
        Плоский список всех файлов в папке на Яндекс.Диске
        :return:
        status_code: str
        result: list[str]
        """
        response = requests.get(f'{self.URL}/files?fields=items.name', headers=self.headers)
        status_code = response.status_code
        result = response.json()['items']
        result = [item['name'] for item in result]
        return status_code, result

    def create_directory(self, timeout=1) -> tuple[int, dict[str, str]]:
        """
        Создание папки на Яндекс.Диске
        :param timeout:
        :return:
        status_code: str
        result: dict
        """
        response = requests.put(f'{self.URL}?path={REMOTE_DIR_PATH}', headers=self.headers)
        time.sleep(timeout)
        status_code = response.status_code
        result = response.json()
        return status_code, result

    def load(self, filename, replace=True) -> int:
        """
        Загрузка файла в папку на Яндекс.Диске
        :param filename: str
        :param replace: bool
        :return:
        status_code: str
        """
        loadfile = os.path.join(LOCAL_DIR_PATH, filename)
        savefile = f"{REMOTE_DIR_PATH}/{filename}"
        res = requests.get(f'{self.URL}/upload'
                           f'?path={savefile}'
                           f'&overwrite={replace}',
                           headers=self.headers)
        response_json = res.json()
        with open(loadfile, 'rb') as file:
            result = requests.put(response_json['href'], files={'file': file})
        return result.status_code

    def upload_files(self, files: list) -> None:
        """
        Пул потоков для загрузки файлов из списка в папку на Яндекс.Диске
        :param files: list
        """
        with ThreadPool(processes=cpu_count()) as pool:
            pool.map(self.load, files)

    def delete(self, filename) -> int:
        """
        Удаление файла из папки на Яндекс.Диске
        :param filename: str
        :return:
        status_code: str
        """
        deleted_file = f"{REMOTE_DIR_PATH}/{filename}"
        result = requests.delete(f'{self.URL}/?path={deleted_file}', headers=self.headers)
        # response_json = result.json()
        return result.status_code

    def delete_files(self, files: list) -> None:
        """
       Пул потоков для удаления файлов из списка в папку на Яндекс.Диске
       :param files: list
       """
        with ThreadPool(processes=cpu_count()) as pool:
            pool.map(self.delete, files)

    def delete_remote_folder(self) -> int:
        """
        Удаление папки на Яндекс.Диске
        :return:
        status_code: str
        """
        result = requests.delete(f'{self.URL}/?path={REMOTE_DIR_PATH}', headers=self.headers)
        return result.status_code


if __name__ == '__main__':
    url = API()
    print(url.check_directory())
    # print(url.create_directory())
    # url.upload_files(["bash.pdf"])
    # print(url.get_info())
    # url.delete_files(['bash.pdf'])
    # print(url.get_info())
