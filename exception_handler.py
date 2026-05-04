import functools
import time
import requests
from requests.exceptions import RequestException

import yandex_API
from settings import app_logger

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


def request_exception_handler(logger=app_logger, max_retries=3, backoff_factor=0.5, timeout=10):
    """Декоратор для безопасного выполнения HTTP-запросов с повторными попытками."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    # Добавляем таймаут по умолчанию, если не указан явно
                    kwargs.setdefault('timeout', timeout)

                    result = func(*args, **kwargs)
                    result.raise_for_status()
                    return result
                except requests.HTTPError as http_err:
                    # Обработка ошибок HTTP-статусов
                    status_code = http_err.response.status_code
                    if status_code in ERRORS:
                        logger.error(f'{status_code} - {ERRORS.get(status_code)}')
                    else:
                        logger.error(f'{status_code} - неизвестная ошибка!!!')
                except (requests.ConnectionError, requests.Timeout) as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Достигнут лимит повторных попыток ({max_retries})")
                        raise

                    # Экспоненциальная задержка
                    wait = backoff_factor * (2 ** (retries - 1))
                    logger.warning(f"Попытка {retries}/{max_retries} не удалась из-за {e.__class__.__name__}. "
                                   f"Повторная попытка через {wait:.1f} сек...")
                    time.sleep(wait)
                except RequestException as e:
                    logger.error(f"Ошибка запроса {e.__class__.__name__}: {e}")
                    raise

        return wrapper

    return decorator


# Пример использования
@request_exception_handler(max_retries=3)
def get_data(timeout):
    yandex_API.API().get_info(timeout=timeout)


class manager:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        print('start enter')
        try:
            raise RuntimeError("test")
        except Exception as ex:
            self.__exit__(type(ex), ex, ex.__traceback__)
            raise ex

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('start exit')


# Пример использования
with manager(r'<path to>.json') as res:
    pass


class SafeSession:
    def __init__(self, base_url=None, timeout=10):
        self.session = requests.Session()
        self.base_url = base_url
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get(self, url_path, **kwargs):
        if self.base_url and not url_path.startswith(('http://', 'https://')):
            url = f"{self.base_url.rstrip('/')}/{url_path.lstrip('/')}"
        else:
            url = url_path

        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")
            raise


# Пример использования
with SafeSession(base_url='https://api.example.com') as session:
    try:
        response = session.get('/users')
        data = response.json()
        print(data)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    get_data()
