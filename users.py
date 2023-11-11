from util import *
import json
import traceback
from config import config
from zzlogger import logger


def load_users(filepath):
    with open(filepath, 'r', encoding="UTF-8") as f:
        return json.load(f)["users"]


def _find_user(all_users, username, password):
    try:
        for u in all_users:
            if u["auth"]["username"] == username:
                password_type = u["auth"].get("passtype", "plain")
                if password_type == "any":
                    return True, u
                elif password_type.lower() in ["plain", "md5", "sha1", "sha256", "sha512"]:
                    hashed_password = calculate_hash(password_type, password)
                    logger.debug("username={}, hashed_password={}", username, hashed_password)
                    if u["auth"]["password"] == hashed_password:
                        return True, u
                else:
                    logger.warning("Not supported password type: {}, please check users.json!", password_type)
    except Exception:
        logger.error("Got an error during find_user, username={}\n{}", username, traceback.format_exc())
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
