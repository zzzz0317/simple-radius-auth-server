import os
import sys
from loguru import logger

DIR_SCRIPT = os.path.dirname(os.path.realpath(sys.argv[0]))
DIR_RUNNING = os.getcwd()

logger.debug("工具存储目录: {}", DIR_SCRIPT)
logger.debug("当前运行目录: {}", DIR_RUNNING)


def get_script_path_file(*sub_path):
    return os.path.join(DIR_SCRIPT, *sub_path)


def get_running_path_file(*sub_path):
    return os.path.join(DIR_RUNNING, *sub_path)

