from util import *
import json
import traceback
from config import config
from zzlogger import logger


def load_users(filepath):
    user_file_path_all = [filepath]
    user_file_path_readed = []
    all_users = {}
    while len(user_file_path_all) > 0:
        user_file_path = user_file_path_all.pop(0)
        if user_file_path in user_file_path_readed:
            continue
        with open(user_file_path, 'r', encoding="UTF-8") as f:
            json_data = json.load(f)
            users = json_data["users"]
            for user in users:
                if user.get("enable", True):
                    all_users[user["auth"]["username"]] = user
            includes = json_data.get("includes", [])
            for inc in includes:
                if inc.get("enable", True) and inc["path"] not in user_file_path_readed:
                    user_file_path_all.append(inc["path"])
        user_file_path_readed.append(user_file_path)
    return all_users


def _find_user(all_users, username, password):
    try:
        if username in all_users.keys():
            u = all_users[username]
            password_type = u["auth"].get("passtype", "plain").lower()
            if password_type == "any":
                return True, u
            elif password_type == "plain":
                if u["auth"]["password"] == password:
                    return True, u
            elif password_type in ["md5", "sha1", "sha256", "sha512"]:
                hashed_password = calculate_hash(password_type, password)
                logger.debug("username={}, hashed_password={}", username, hashed_password)
                if u["auth"]["password"] == hashed_password:
                    return True, u
            elif password_type == "argon2":
                if argon2_verify(u["auth"]["password"], password):
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
    print(find_user("test1", "test1"))
    print(find_user("111", "123"))
    print(find_user("test2", "test2"))
