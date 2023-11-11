import sys

from loguru import logger
from config import config


def setup_loguru():
    logger.remove()
    logger_level = config.get("logger_level", "INFO")
    logger.add(sys.stderr, level=logger_level)
    logger.debug("Logger level: {}", logger_level)


setup_loguru()
