from util import *
import json
import traceback
from loguru import logger
from config import config


def load_users(filepath):
    with open(filepath, 'r', encoding="UTF-8") as f:
        return json.load(f)["users"]


def _find_user(all_users, username, password):
    try:
        for u in all_users:
            if u["auth"]["username"] == username:
                if u["auth"]["password"] == password:
                    return True, u["reply_attr"]
    except Exception:
        logger.error("Got an error during find_user, username={}, password={}\n{}", username, password,
                     traceback.format_exc())
    return False, {}


def find_user(username, password):
    users = load_users(get_script_path_file("users.json"))
    return _find_user(users, username, password)


if __name__ == '__main__':
    # print(json.dumps(users, ensure_ascii=False, indent=4))
    print(find_user("111", "111"))
    from time import sleep
    sleep(5)
    print(find_user("111", "123"))
