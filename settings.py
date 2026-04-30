"""
    настройки переменных окружения .env
"""
import os
import configparser
from loguru import logger as app_logger


config = configparser.ConfigParser()

if os.path.exists('config.ini'):
    config.read('config.ini')
else:
    print("РАБОТА НЕВОЗМОЖНА!!! \n\t->\t Переменные окружения не загружены т.к отсутствует файл 'config.ini'")
    exit(-1)

LOCAL_DIR_PATH = config['default']['LOCAL_DIR_PATH']
if not os.path.exists(LOCAL_DIR_PATH):
    print('РАБОТА НЕВОЗМОЖНА!!! \n\t->\tЛокальная папка не найдена! Укажите корректный путь в файле "config.ini"')
    exit(-1)

HOST_API = config['default']["HOST_API"]
API_KEY = config['default']["API_KEY"]
REMOTE_DIR_PATH = config['default']['REMOTE_DIR_PATH']
SYNCHRONIZATION_PERIOD = config['default']['SYNCHRONIZATION_PERIOD']

LOG_FILE = config['default']['LOG_FILE']
app_logger.add(LOG_FILE, format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {file}:{line} - '{message}'")

DATA_FILE = 'data.pkl'
