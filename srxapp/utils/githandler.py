import os
import shutil
import git
import logging

from srxapp.utils import helpers

logger = logging.getLogger(__name__)


class Repo:
    def __init__(self, request):
        self.remote_repo = os.environ.get("YM_ANSIBLEREPO", "")
        self.username = request.user.get_username()
        self.workspace = "workspace/" + self.username
        if os.path.isdir(self.workspace):
            self.local_repo = git.Repo(self.workspace)

    def git_clone(self):
        try:
            if os.path.isdir(self.workspace):
                shutil.rmtree(self.workspace)

            logger.info("Cloning git repository...")
            git.Repo.clone_from(self.remote_repo, self.workspace)
            return "success"

        except Exception:
            return helpers.view_exception(Exception)

    def git_get_diff(self):
        try:
            return self.local_repo.git.diff()

        except Exception:
            helpers.view_exception(Exception)

    def git_commit(self):
        try:
            file_to_commit = os.environ.get("YM_YAMLFILE", "")
            commit_message = "SRX YAMLr firewall policy change"

            logger.info("Committing config")
            self.local_repo.git.add(file_to_commit)
            self.local_repo.git.commit(m=commit_message)

        except Exception:
            helpers.view_exception(Exception)

    def git_push(self, token):
        try:
            def compose_address_with_token(urlprefix):
                repo = self.remote_repo.replace(urlprefix, "")
                return urlprefix + token + "@" + repo

            if self.remote_repo.startswith("https"):
                address = compose_address_with_token("https://")
            else:
                address = compose_address_with_token("http://")

            logger.info("Pushing config to {}...".format(self.remote_repo))
            self.local_repo.git.pull()
            if self.username == "testuser":
                self.local_repo.git.push("-n", address)
            else:
                self.local_repo.git.push(address)
            return "success"

        except Exception:
            return helpers.view_exception(Exception)
