import os
import re
import json
import base64
import hashlib
import logging
import traceback
import srxpolbld

from ruamel.yaml import YAML
from django.utils.encoding import force_text
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def get_baseapp_context(request):
    user = User.objects.get(username=request.user.username)
    token_set = check_if_token_set(user)
    try:
        host_var_file_path = srxpolbld.models.HostVarFilePath.objects.get(id=0).path
    except Exception:
        host_var_file_path = None

    with open("version") as vfile:
        version = vfile.read()
    context = {
        "username": user,
        "token_set": token_set,
        "version": version,
        "host_var_file_path": host_var_file_path,
    }
    return context


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


def get_hash(dict_):
    string = json.dumps(dict_, sort_keys=True).encode('utf-8')
    return hashlib.md5(string).hexdigest()


def get_django_secret():
    secret = os.environ.get("YM_DJANGOSECRET", "")
    return force_text(secret)


def check_if_token_set(user):
    dbstring = user.usersettings.gogs_tkn
    return False if dbstring == "" else True


def get_token(request):
    try:
        user = User.objects.get(username=request.user.username)
        token_encrypted = user.usersettings.gogs_tkn
        token = decode_string(token_encrypted)
        return token
    except Exception:
        return "Token could not be retrieved"


def in_string(word):
    """
    Check if string_a matches whole word in string_b, not only sequence of
    characters as if using 'if string_a in string_b'.

        >>> in_string('word')('one word of many')  ## return 'word'
        >>> in_string('word')('swordsmith')        ## return None
    """
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search


def encode_string(string):
    """
    Encode a string with the django secret.
    """
    try:
        key = get_django_secret()

        encoded_str_list = []
        for string_position in range(len(string)):
            key_char = key[string_position % len(key)]
            unicode_number = ord(string[string_position])
            unicode_number_keyencoded = unicode_number + ord(key_char)
            unicode_string = chr(unicode_number_keyencoded)
            encoded_str_list.append(unicode_string)

        str_of_encoded_unicode_strings = "".join(encoded_str_list)
        encoded_str_binary = str_of_encoded_unicode_strings.encode("utf-8")
        encoded_str_bin_b64 = base64.urlsafe_b64encode(encoded_str_binary)
        encoded_str_for_storage = encoded_str_bin_b64.decode("utf-8")
        return encoded_str_for_storage

    except Exception:
        logger.error(traceback.format_exc())


def decode_string(encoded):
    """
    Decode a string that was encoded with the django secret.
    """
    try:
        key = get_django_secret()

        encoded_str_b64 = encoded.encode("utf-8")
        encoded_str_bin = base64.urlsafe_b64decode(encoded_str_b64)
        str_of_encoded_unicode_strings = encoded_str_bin.decode("utf-8")

        decoded_str_list = []
        for string_position in range(len(str_of_encoded_unicode_strings)):
            key_char = key[string_position % len(key)]
            unicode_number = ord(str_of_encoded_unicode_strings[string_position])
            unicode_number_keydecoded = unicode_number - ord(key_char)
            unicode_string = chr(unicode_number_keydecoded)
            decoded_str_list.append(unicode_string)

        decoded_string = "".join(decoded_str_list)
        return decoded_string

    except Exception:
        logger.error(traceback.format_exc())


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
