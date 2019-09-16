import os
import shutil
import git
import logging
import urllib3

from baseapp import helpers
from . import REMOTE_REPO_URL

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


class Repo:
    def __init__(self, request, auto_enable_workspace=True):
        self.request = request
        self.username = request.user.username
        self.useremail = request.user.email
        self.workspace = "workspace/" + self.username
        if auto_enable_workspace is True:
            self.git_enable_workspace()

    def git_clone(self):
        try:
            if os.path.isdir(self.workspace):
                shutil.rmtree(self.workspace)

            logger.info("Cloning git repository...")
            git.Repo.clone_from(
                REMOTE_REPO_URL, self.workspace,
                config="http.sslVerify=false",
            )
            return "success"

        except Exception:
            helpers.view_exception(Exception)
            return "clone_failed"

    def git_enable_workspace(self):
        try:
            self.local_repo = git.Repo(self.workspace)
        except Exception:
            return helpers.view_exception(Exception)

    def git_config(self):
        try:
            with self.local_repo.config_writer() as cw:
                cw.set_value("user", "name", self.username).release()
                cw.set_value("user", "email", self.useremail).release()

        except Exception:
            return helpers.view_exception(Exception)

    def get_srcfile_commithash(self):
        try:
            yamlfile = os.environ.get("YM_YAMLFILE", "")
            commit_hash = self.local_repo.git.log(
                "-n 1", "--pretty=format:%H", "--", yamlfile
            )
            return commit_hash

        except Exception:
            helpers.view_exception(Exception)

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

    def get_git_push_address(self):
        try:
            token = helpers.get_token(self.request)
            prfx = "https://" if REMOTE_REPO_URL.startswith("https") else "http://"
            repo = REMOTE_REPO_URL.replace(prfx, "")
            # Put colon behind token to prevent gogs from opening a stdin
            # prompt asking for a password in case of invalid token.
            return prfx + token + ":" + "@" + repo

        except Exception:
            helpers.view_exception(Exception)

    def git_push(self):
        try:
            address = self.get_git_push_address()

            self.local_repo.git.pull()

            logger.info("Pushing config to {}...".format(REMOTE_REPO_URL))
            if self.username != "unittest_user":
                self.local_repo.git.push(address)
            else:
                self.local_repo.git.push("-n", address)
            return "success"

        except Exception as exc_instance:
            error = str(exc_instance)
            if "HTTP 401" in error:
                return "unauthorized"
            else:
                return helpers.view_exception(Exception)
