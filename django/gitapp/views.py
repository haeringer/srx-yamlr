from django.core.cache import cache
from django.http import JsonResponse

from baseapp import helpers
from . import githandler


def clone_repo(request):
    try:
        repo = githandler.Repo(request)
        response = repo.git_clone()
        repo.git_config()
        commithash_current_data = repo.get_file_commit_hash()
        cache.set("commithash_current_data", commithash_current_data)
    except Exception:
        helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def commit_config(request):
    try:
        repo = githandler.Repo(request)
        repo.git_commit()
        response = repo.git_push()
        if response == "success":
            request.session["configdict"] = {}

    except Exception:
        helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
