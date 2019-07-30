import os
import re
import json
import logging
import traceback

from ruamel.yaml import YAML
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from simplecrypt import encrypt, decrypt
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


def encrypt_string(string):
    key = get_django_secret()

    cipher = encrypt(key, string)
    encoded_cipher = b64encode(cipher)
    return encoded_cipher.decode("utf-8")


def decrypt_string(string):
    key = get_django_secret()

    cipher = b64decode(string)
    plain_text = decrypt(key, cipher)
    return plain_text.decode("utf-8")


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
