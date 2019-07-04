import os
import shutil
import git
import logging

from srxapp.utils import const, helpers

logger = logging.getLogger(__name__)


class Repo:

    def __init__(self):
        self.remote_repo = os.environ.get('YM_ANSIBLEREPO', '')
        if os.path.isdir(const.WORKSPACE):
            self.local_repo = git.Repo(const.WORKSPACE)

    def git_clone(self):
        try:
            if os.path.isdir(const.WORKSPACE):
                shutil.rmtree(const.WORKSPACE)

            logger.info('Cloning git repository...')
            git.Repo.clone_from(self.remote_repo, const.WORKSPACE)

        except Exception:
            helpers.view_exception(Exception)

    def git_get_diff(self):
        try:
            return self.local_repo.git.diff()
        except Exception:
            helpers.view_exception(Exception)

    def git_commit(self):
        try:
            file_to_commit = os.environ.get('YM_YAMLFILE', '')
            commit_message = 'SRX YAMLr firewall policy change'

            logger.info('Committing config')
            self.local_repo.git.add(file_to_commit)
            self.local_repo.git.commit(m=commit_message)

        except Exception:
            helpers.view_exception(Exception)

    def git_push(self, token):
        try:
            def compose_url_with_token(urlprefix):
                repo = self.remote_repo.replace(urlprefix, '')
                return urlprefix + token + '@' + repo

            if self.remote_repo.startswith('https'):
                address = compose_url_with_token('https://')
            else:
                address = compose_url_with_token('http://')

            logger.info('Pushing config to {}...'.format(self.remote_repo))
            self.local_repo.git.fetch()
            self.local_repo.git.push('-n', address)
            return 'success'

        except Exception:
            return helpers.view_exception(Exception)
