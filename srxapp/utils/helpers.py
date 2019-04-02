import os
import json
import git
import oyaml as yaml
import logging
import traceback
import requests

from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode

logger = logging.getLogger(__name__)


def git_clone_to_workspace():
    git_url = os.environ.get('YM_GIT_URL', '')

    # abuse try/except for logic because git.Repo does not
    # provide proper return values if it doesn't succeed
    try:
        repo = git.Repo('workspace')
    except Exception:
        repo = None

    if repo:
        logger.info('Updating repo...')
        remote_repo = repo.remotes.origin
        remote_repo.pull()
    else:
        logger.info('Cloning repo...')
        git.Repo.clone_from(git_url, 'workspace')


def view_exception(Exception):
    logger.error(traceback.format_exc())
    return dict(error=json.dumps(traceback.format_exc()))


def log_config(configdict):
    logger.debug('Session configdict:\n  {}\n'.format(configdict))


def convert_dict_to_yaml(dictionary):
    return dict(yamlconfig=yaml.dump(dictionary, default_flow_style=False))


def get_jenkins_session_object():
    jnk_user = os.environ.get('YM_JENKINS_USER', '')
    jnk_tkn = os.environ.get('YM_JENKINS_TOKEN', '')

    session = requests.Session()
    session.auth = (jnk_user, jnk_tkn)
    session.verify = False

    return session


def get_jenkins_job_url(commit):
    jnk_url = os.environ.get('YM_JENKINS_URL', '')
    jnk_job = os.environ.get('YM_JENKINS_JOB', '')
    job_url = '{}/job/{}/buildWithParameters?commit={}'.format(
        jnk_url, jnk_job, commit)

    return job_url


def dict_with_sorted_list_values(**kwargs):
    new_dict = {}

    for key, values in kwargs.items():
        if isinstance(values, list):
            new_dict[key] = sorted(values)
        else:
            new_dict[key] = values

    return new_dict


def encrypt_string(string):
    key = os.environ.get('YM_DJANGOSECRET', '')

    cipher = encrypt(key, string)
    encoded_cipher = b64encode(cipher)
    return encoded_cipher.decode('utf-8')


def decrypt_string(string):
    key = os.environ.get('YM_DJANGOSECRET', '')

    cipher = b64decode(string)
    plain_text = decrypt(key, cipher)
    return plain_text.decode('utf-8')
