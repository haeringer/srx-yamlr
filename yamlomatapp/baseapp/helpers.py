import os
import re
import json
import hashlib
import logging
import traceback

from ruamel.yaml import YAML
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64encode, b64decode

logger = logging.getLogger(__name__)
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def view_exception(Exception):
    logger.error(traceback.format_exc())
    return dict(error=json.dumps(traceback.format_exc()))


def log_config(configdict):
    logger.debug("Session configdict:\n  {}\n".format(configdict))


def convert_dict_to_yaml(dictionary):
    with open("/tmp/srx-yamlr_tmp", "w") as stream:
        yaml.dump(dictionary, stream)

    with open("/tmp/srx-yamlr_tmp", "r") as stream:
        yamlconfig = stream.read()

    return dict(yamlconfig=yamlconfig)


def dict_with_sorted_list_values(**kwargs):
    new_dict = {}

    for key, values in kwargs.items():
        if isinstance(values, list):
            new_dict[key] = sorted(values)
        else:
            new_dict[key] = values

    return new_dict


def get_django_secret():
    secret = os.environ.get("YM_DJANGOSECRET", "")
    return force_text(secret)


def check_if_token_set(user):
    dbstring = user.usersettings.gogs_tkn

    if dbstring == "":
        return False
    else:
        return True


def get_token(request):
    user = User.objects.get(username=request.user.username)
    token_encrypted = user.usersettings.gogs_tkn
    token = decrypt_string(token_encrypted)
    return token


def in_string(word):
    """
    Check if string_a matches whole word in string_b, not only sequence of
    characters as if using 'if string_a in string_b'.

        >>> in_string('word')('one word of many')  ## return 'word'
        >>> in_string('word')('swordsmith')        ## return None
    """
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search


def pad(string, size):
    return string + (size - len(string) % size) * chr(size - len(string) % size)


def unpad(string):
    return string[:-ord(string[len(string) - 1:])]


def encrypt_string(string):
    password = get_django_secret()
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    str_padded = pad(string, 16).encode("utf8")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    encoded_cipher = b64encode(iv + cipher.encrypt(str_padded))
    return encoded_cipher.decode("utf-8")


def decrypt_string(encrypted):
    password = get_django_secret()
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    enc_decoded = b64decode(encrypted)
    iv = enc_decoded[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(enc_decoded[16:]))
    return bytes.decode(decrypted)


def search_object_in_workingdict(request):
    searchtype = request.GET.get("searchtype", None)
    inp = request.GET.get("input", None)
    wd = request.session["workingdict"]
    response = []

    if searchtype == "from" or searchtype == "to":
        singleobjects = "addresses"
        setobjects = "addrsets"
    elif searchtype == "app":
        singleobjects = "applications"
        setobjects = "appsets"

    for obj in wd[singleobjects]:
        if inp in obj["name"].upper() or inp in obj["val"].upper():
            response.append(obj)

    for obj in wd[setobjects]:
        if inp in obj["name"].upper():
            response.append(obj)
        else:
            for val in obj["val"]:
                if inp in val.upper():
                    response.append(obj)
                    break
    return response
