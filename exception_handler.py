import functools
import time
import requests
from requests.exceptions import RequestException
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
# @request_exception_handler(max_retries=3)
# def get_data(timeout):
#     yandex_API.API().get_info(timeout=timeout)


class SafeRequest:
    """Контекстный менеджер для безопасного выполнения HTTP-запросов с повторными попытками."""
    def __init__(self, method, url, **kwargs):
        self.session = requests.Session()
        self.method = method
        self.url = url
        self.kwargs = kwargs

    def __enter__(self):
        retries = 0
        max_retries = 10
        backoff_factor = 0.3
        try:
            self.kwargs.setdefault('timeout', 10)
            response = getattr(self.session, self.method)(self.url, **self.kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            # Обработка ошибок HTTP-статусов
            status_code = e.response.status_code
            if status_code in ERRORS:
                app_logger.error(f'{status_code} - {ERRORS.get(status_code)}')
            else:
                app_logger.error(f'{status_code} - неизвестная ошибка!!!')
            self.__exit__(type(e), e, e.__traceback__)
        except (requests.ConnectionError, requests.Timeout) as e:
            retries += 1
            if retries > max_retries:
                app_logger.error(f"Достигнут лимит повторных попыток ({max_retries})")
                self.__exit__(type(e), e, e.__traceback__)

            # Экспоненциальная задержка
            wait = backoff_factor * (2 ** (retries - 1))
            app_logger.warning(f"Попытка {retries}/{max_retries} не удалась из-за {e.__class__.__name__}. "
                               f"Повторная попытка через {wait:.1f} сек...")
            time.sleep(wait)
        except RequestException as e:
            app_logger.error(f"Ошибка запроса {e.__class__.__name__}: {e}")
            self.__exit__(type(e), e, e.__traceback__)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        return True


if __name__ == '__main__':
    with SafeRequest(method='get',
                     url='https://cloud-api.yandex.net/v1/disk/resources/56?path=_yadisk&fields=_embedded.items.name',
                     headers={'Content-Type': 'application/json',
                              'Accept': 'application/json',
                              'Authorization': f'OAuth y0__wgBEMqq3ggY25YDIMGymZoXMPCfvdoH7_p0DAlBFxPtrD8MTDCp2n5Q4Lg'},
                     timeout=10) as session:
        status_code = session.status_code
        result = session.json()
    print(status_code)
    print(result)
