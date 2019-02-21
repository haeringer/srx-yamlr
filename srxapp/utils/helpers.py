import os
import json
import git
import oyaml as yaml
import logging
import traceback

logger = logging.getLogger(__name__)


def git_clone_to_workspace():
    git_url = os.environ.get('YAMLOMAT_GIT_URL', '')

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


def queryset_to_var(queryset):
    '''
    Convert django queryset to string or list, depending on queryset content
    '''
    if queryset:
        if len(queryset) > 1:
            rval = []
            for q in queryset:
                rval.append(q.name)
        else:
            rval = queryset[0].name
    else:
        rval = ''
    return rval


def view_exception(Exception):
    logger.error(traceback.format_exc())
    return dict(error=json.dumps(traceback.format_exc()))


def convert_dict_to_yaml(dictionary):
    return dict(yamlconfig=yaml.dump(dictionary, default_flow_style=False))