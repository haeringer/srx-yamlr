import os
import shutil
import git
import logging
import requests
import urllib3

from baseapp import helpers

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


class Repo:
    def __init__(self, request):
        self.request = request
        self.git_server = os.environ.get("YM_GITSERVER", "")
        self.remote_repo = os.environ.get("YM_ANSIBLEREPO", "")
        self.remote_repo_url = os.path.join(self.git_server, self.remote_repo)
        self.username = request.user.username
        self.useremail = request.user.email
        self.workspace = "workspace/" + self.username
        if os.path.isdir(self.workspace):
            self.local_repo = git.Repo(self.workspace)

    def git_clone(self):
        try:
            if os.path.isdir(self.workspace):
                shutil.rmtree(self.workspace)

            logger.info("Cloning git repository...")
            git.Repo.clone_from(
                self.remote_repo_url, self.workspace,
                config="http.sslVerify=false",
            )
            self.local_repo = git.Repo(self.workspace)
            return "success"

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
            prfx = "https://" if self.remote_repo_url.startswith("https") else "http://"
            repo = self.remote_repo_url.replace(prfx, "")
            # Put colon behind token to prevent gogs from opening a stdin
            # prompt asking for a password in case of invalid token.
            return prfx + token + ":" + "@" + repo

        except Exception:
            helpers.view_exception(Exception)

    def validate_git_authorization(self):
        try:
            token = helpers.get_token(self.request)
            api_url = os.path.join(self.git_server, "api/v1/repos/", self.remote_repo)
            headers = {"Authorization": "token {}".format(token)}
            return requests.get(api_url, headers=headers, verify=False)

        except Exception:
            helpers.view_exception(Exception)

    def git_push(self):
        try:
            address = self.get_git_push_address()
            response = self.validate_git_authorization()

            self.local_repo.git.pull()

            logger.info("Pushing config to {}...".format(self.remote_repo_url))
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
