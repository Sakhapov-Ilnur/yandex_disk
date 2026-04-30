from settings import app_logger, LOCAL_DIR_PATH
from synchronization import Synchronization


if __name__ == '__main__':
    app_logger.info(f'Начата синхронизация папки "{LOCAL_DIR_PATH}"\n')
    app = Synchronization()
    app.check_resources()
    app.start()
