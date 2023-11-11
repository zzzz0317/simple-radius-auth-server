import hashlib
import os
import sys

DIR_SCRIPT = os.path.dirname(os.path.realpath(sys.argv[0]))
DIR_RUNNING = os.getcwd()


def get_script_path_file(*sub_path):
    return os.path.join(DIR_SCRIPT, *sub_path)


def get_running_path_file(*sub_path):
    return os.path.join(DIR_RUNNING, *sub_path)


def calculate_hash(algorithm: str, data: str):
    algorithm = algorithm.lower()
    if algorithm == 'plain':
        return data
    elif algorithm == 'md5':
        hash_object = hashlib.md5()
    elif algorithm == 'sha1':
        hash_object = hashlib.sha1()
    elif algorithm == 'sha256':
        hash_object = hashlib.sha256()
    elif algorithm == 'sha512':
        hash_object = hashlib.sha512()
    else:
        raise Exception("Hash algorithm not supported")
    hash_object.update(data.encode('utf-8'))
    return hash_object.hexdigest()
