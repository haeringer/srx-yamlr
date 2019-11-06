import os
import re
import json
import base64
import hashlib
import logging
import traceback
import srxapp

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
        host_var_file_path = srxapp.models.HostVarFilePath.objects.get(id=0).path
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
    try:
        key = get_django_secret()
        enc = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(string[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()
    except Exception:
        logger.error(traceback.format_exc())


def decode_string(encoded):
    try:
        key = get_django_secret()
        dec = []
        encoded = base64.urlsafe_b64decode(encoded).decode()
        for i in range(len(encoded)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(encoded[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)
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
