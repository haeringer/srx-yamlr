from django.http import JsonResponse

from baseapp import helpers
from . import githandler


def clone_repo(request):
    try:
        response = {}
        repo = githandler.Repo(request, auto_enable_workspace=False)
        response["clone_result"] = repo.git_clone()
        repo.git_enable_workspace()
        repo.git_config()
        response["srcfile_commithash"] = repo.get_srcfile_commithash()
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def commit_config(request):
    try:
        repo = githandler.Repo(request)
        repo.git_commit()
        response = repo.git_push()
        if response == "success":
            request.session["configdict"] = {}

    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
