from util import *
import json


def load_config(filepath):
    with open(filepath, 'r', encoding="UTF-8") as f:
        return json.load(f)


config = load_config(get_script_path_file("config.json"))

if __name__ == '__main__':
    print(json.dumps(config, ensure_ascii=False, indent=4))
