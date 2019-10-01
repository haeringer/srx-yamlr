import os
import shutil
import git
import logging
import urllib3
from django.http import JsonResponse

from baseapp import helpers
from . import REMOTE_REPO_URL, WORKSPACEDIR

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


def clone_repo(request):
    """
    Clone a Git repository from given remote address into a local workspace directory.
    Git user configuration is set from user information within request.
    """
    try:
        username = request.user.username
        useremail = request.user.email
        workspace = WORKSPACEDIR + username

        if os.path.isdir(workspace):
            shutil.rmtree(workspace)

        logger.info("Cloning git repository...")
        git.Repo.clone_from(
            REMOTE_REPO_URL, workspace,
            config="http.sslVerify=false",
        )

        local_repo = get_local_repo(request)
        with local_repo.config_writer() as cw:
            cw.set_value("user", "name", username).release()
            cw.set_value("user", "email", useremail).release()

        response = "success"
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def commithash(request):
    """
    Retrieve the latest commit hash value from a given file or repository.

    If a file path is provided, the value from that file is returned.
    Otherwise, the value from the current repository is returned.

    Provide "file_path" in request data as a relative path within the current repo:

    { "file_path": "relative/path/to/file" }
    """
    try:
        file_path = request.GET.get("file_path", None)
        local_repo = get_local_repo(request)

        if file_path:
            commit_hash = local_repo.git.log(
                "-n 1", "--pretty=format:%H", "--", file_path
            )
        else:
            commit_hash = local_repo.git.rev_parse("--verify HEAD")

        response = commit_hash
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def get_diff(request):
    """
    Return the Git diff output from the repository within the workspace
    directory of the requesting user.
    """
    try:
        local_repo = get_local_repo(request)
        response = local_repo.git.diff()
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def commit_config(request):
    """
    Commit the file provided within the request and push to the remote
    repository.
    """
    try:
        file_to_commit = request.POST.get("host_var_file_path", None)
        username = request.user.username
        local_repo = get_local_repo(request)

        local_repo.git.pull()
        local_repo.git.add(file_to_commit)
        logger.info("Committing config")
        local_repo.git.commit(m="SRX YAMLr firewall policy change")

        address = get_git_push_address(request)
        logger.info("Pushing config to {}...".format(REMOTE_REPO_URL))
        if username != "unittest_user":
            local_repo.git.push(address)
        else:
            local_repo.git.push("-n", address)
        request.session["configdict"] = {}
        response = "success"

    except Exception as exc_instance:
        error = str(exc_instance)
        if "HTTP 401" in error:
            logger.info("Invalid token: {}".format(helpers.get_token(request)))
            response = "unauthorized"
        else:
            response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def get_local_repo(request):
    """
    Return the Git repository which resides within the workspace
    directory of the requesting user as a git object.
    """
    try:
        workspace = WORKSPACEDIR + request.user.username
        local_repo = git.Repo(workspace)
        return local_repo
    except Exception:
        helpers.view_exception(Exception)


def get_git_push_address(request):
    """
    Assemble the Git push address from user token, server url and repository.
    """
    try:
        token = helpers.get_token(request)
        prfx = "https://" if REMOTE_REPO_URL.startswith("https") else "http://"
        repo = REMOTE_REPO_URL.replace(prfx, "")
        # Put colon behind token to prevent gogs from opening a stdin
        # prompt asking for a password in case of invalid token.
        return prfx + token + ":" + "@" + repo
    except Exception:
        helpers.view_exception(Exception)
