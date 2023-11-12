import sys
from util import *

hash_method = None
password = None
from_cmd = False
if len(sys.argv) == 3:
    from_cmd = True
    hash_method = sys.argv[1]
    password = sys.argv[2]

if hash_method is None:
    print("Supported hash method: MD5 SHA1 SHA256 SHA512 Argon2")
    while hash_method is None:
        hash_method = input("Please select a hash method: [Argon2]")
        hash_method = hash_method.lower()
        if hash_method == "":
            hash_method = "argon2"
        elif hash_method not in ["md5", "sha1", "sha256", "sha512", "argon2"]:
            print("Hash method not found")
            hash_method = None

if password is None:
    password = input("Please input a password:\n")

if not from_cmd:
    print("Hash result:")
if hash_method in ["md5", "sha1", "sha256", "sha512"]:
    print(calculate_hash(hash_method, password))
elif hash_method == "argon2":
    print(argon2_hash(password))
