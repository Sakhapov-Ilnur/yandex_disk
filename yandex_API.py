"""
    Модуль взаимодействия с API yandex.диска
"""
import os.path
import time
from settings import HOST_API, API_KEY, LOCAL_DIR_PATH, REMOTE_DIR_PATH, app_logger
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from exception_handler import SafeRequest


class API:
    """
        Класс взаимодействия с папкой на Яндекс.Диске
    """
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
        with SafeRequest(method='get', url=f'{self.URL}?path={REMOTE_DIR_PATH}',
                         headers=self.headers,
                         timeout=5) as response:
            status_code = response.status_code
            result = response.json()

        return status_code, result

    def get_info(self, timeout=5) -> tuple[int, list[str]]:
        """
        Список всех файлов в папке на Яндекс.Диске
        :return:
        status_code: str
        result: list[str]
        """
        with SafeRequest(method='get', url=f'{self.URL}?path={REMOTE_DIR_PATH}&fields=_embedded.items.name',
                         headers=self.headers, timeout=timeout) as response:
            status_code = response.status_code
            result = response.json()['_embedded']['items']
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
        with SafeRequest(method='put', url=f'{self.URL}?path={REMOTE_DIR_PATH}', headers=self.headers) as response:
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
        with SafeRequest(method='get', url=f'{self.URL}/upload?path={savefile}&overwrite={replace}',
                         headers=self.headers) as response:
            response_json = response.json()
            with open(loadfile, 'rb') as file:
                with SafeRequest(method='put', url=response_json['href'], files={'file': file}) as result:
                    status_code = result.status_code
        return status_code

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
        with SafeRequest(method='delete', url=f'{self.URL}/?path={deleted_file}', headers=self.headers) as response:
            result = response.status_code
        return result

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
        with SafeRequest(method='delete', url=f'{self.URL}/?path={REMOTE_DIR_PATH}', headers=self.headers) as response:
            result = response.status_code
        return result


if __name__ == '__main__':
    url = API()
    print(url.check_directory())
    print(url.get_info())
    # print(url.create_directory())
    # url.upload_files(["bash.pdf"])
    # print(url.get_info())
    # url.delete_files(['bash.pdf'])
    # print(url.get_info())
