import hashlib
import os
import sys

import argon2

DIR_SCRIPT = os.path.dirname(os.path.realpath(sys.argv[0]))
DIR_RUNNING = os.getcwd()

argon2_password_hasher = argon2.PasswordHasher()


def get_script_path_file(*sub_path):
    return os.path.join(DIR_SCRIPT, *sub_path)


def get_running_path_file(*sub_path):
    return os.path.join(DIR_RUNNING, *sub_path)


def calculate_hash(algorithm: str, data: str):
    algorithm = algorithm.lower()
    if algorithm == 'md5':
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


def argon2_hash(password: str):
    return argon2_password_hasher.hash(password)


def argon2_verify(hashed_password: str, password: str):
    try:
        return argon2_password_hasher.verify(hashed_password, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
