"""
    настройки переменных окружения .env
"""
import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger as app_logger


if find_dotenv():
    load_dotenv()
else:
    print("РАБОТА НЕВОЗМОЖНА!!! \n\t->\t Переменные окружения не загружены т.к отсутствует файл '.env'")
    exit(-1)

LOCAL_DIR_PATH = os.getenv("LOCAL_DIR_PATH")
if not os.path.exists(LOCAL_DIR_PATH):
    print('РАБОТА НЕВОЗМОЖНА!!! \n\t->\tЛокальная папка не найдена! Укажите корректный путь в файле .env')
    exit(-1)

HOST_API = os.getenv("HOST_API")
API_KEY = os.getenv("API_KEY")
REMOTE_DIR_PATH = os.getenv('REMOTE_DIR_PATH')
SYNCHRONIZATION_PERIOD = os.getenv('SYNCHRONIZATION_PERIOD')

LOG_FILE = os.getenv('LOG_FILE')
app_logger.add(LOG_FILE, format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {file}:{line} - '{message}'")

DATA_FILE = 'data.pkl'
