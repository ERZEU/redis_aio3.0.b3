from loguru import logger
from datetime import date


def write_log_files():
    logger.add(f'logging/{date.today()}.log',
                    format="{time} {level} {message}",
                    level="DEBUG",
                    rotation='00:00',
                    compression='zip')



