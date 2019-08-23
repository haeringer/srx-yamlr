from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache

from srxapp.utils import config, helpers, source, githandler


@login_required(redirect_field_name=None)
def main_view(request):
    try:
        user = User.objects.get(username=request.user.username)
        token_set = helpers.check_if_token_set(user)
        with open("version") as vfile:
            version = vfile.read()
        context = {
            "username": request.user.username,
            "token_set": token_set,
            "version": version,
        }
    except Exception:
        helpers.view_exception(Exception)
        raise Http404("HTTP 404 Error")
    return render(request, "srxapp/main.html", context)


def create_session_stores(request):
    try:
        workingdict_origin = cache.get("workingdict_origin")
        commithash_cached_data = cache.get("commithash_cached_data")
        if workingdict_origin and commithash_cached_data:
            request.session["workingdict"] = workingdict_origin
            commithash_current_data = cache.get("commithash_current_data")
            if commithash_cached_data == commithash_current_data:
                response = "cache_ok"
            else:
                response = "cache_update"
        else:
            response = "cache_update"
        request.session["configdict"] = {}
        request.session["pe_detail"] = {}
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def load_objects(request):
    try:
        src = source.sourceData(request)
        src.read_source_file()
        src.import_zones()
        src.import_addresses()
        src.import_addrsets()
        src.import_applications()
        src.import_appsets()
        src.import_policies()
        src.save_dict_to_cache()
        request.session["workingdict"] = cache.get("workingdict_origin")

        commithash_current_data = cache.get("commithash_current_data")
        cache.set("commithash_cached_data", commithash_current_data)
        response = "success"
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def clone_repo(request):
    try:
        repo = githandler.Repo(request)
        response = repo.git_clone()
        repo.git_config()

        commithash_current_data = repo.get_file_commit_hash()
        cache.set("commithash_current_data", commithash_current_data)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def load_modalcontent(request):
    try:
        workingdict = request.session["workingdict"]
        context = {
            "zones": workingdict["zones"],
            "addresses": workingdict["addresses"],
            "applications": workingdict["applications"],
        }
    except Exception:
        raise Http404("HTTP 404 Error")
    return render(request, "srxapp/modalcnt-create.html", context)


def search_object(request):
    try:
        response = helpers.search_object_in_workingdict(request)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_add_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.add_address()
        if "p_exists" not in result:
            request.session["configdict"] = result
            response = helpers.convert_dict_to_yaml(result)
        else:
            request.session["configdict"] = result["p_existing"]
            request.session["pe_detail"] = result["pe_detail"]
            response = "p_exists"
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.delete_address()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_add_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.add_application()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.delete_application()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_address(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_address()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_addrset(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_addrset()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_application(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_application()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_appset(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_appset()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_rename(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.update_policyname()
        request.session["configdict"] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def filter_objects(request):
    selectedzone = request.GET.get("selectedzone", None)
    if selectedzone == "Choose Zone...":
        return JsonResponse(None, safe=False)

    workingdict = request.session["workingdict"]

    addresses_filtered = []
    for address in workingdict["addresses"]:
        if address["zone"] == selectedzone:
            addresses_filtered.append(address["name"])

    response = dict(addresses=addresses_filtered)
    return JsonResponse(response, safe=False)


def write_yamlconfig(request):
    try:
        src = source.sourceData(request)
        src.update_source_file()
        repo = githandler.Repo(request)
        response = repo.git_get_diff()
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


def get_yamlconfig(request):
    response = helpers.convert_dict_to_yaml(request.session["configdict"])
    return JsonResponse(response, safe=False)


def get_existing_policy_details(request):
    response = request.session["pe_detail"]
    return JsonResponse(response, safe=False)


def set_token_gogs(request):
    try:
        user = User.objects.get(username=request.user.username)
        token = request.POST.get("token", None)
        token_encrypted = helpers.encrypt_string(token)
        user.usersettings.gogs_tkn = token_encrypted
        user.save()
        response = 0
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def check_token_gogs(request):
    try:
        user = User.objects.get(username=request.user.username)
        response = helpers.check_if_token_set(user)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def check_session_status(request):
    try:
        response = 0 if request.session._get_session_key() else 1
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def extend_session(request):
    try:
        request.session.set_expiry(900)
        response = 0
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def set_new_password(request):
    try:
        user = User.objects.get(username=request.user.username)
        password = request.POST.get("password")
        user.set_password(password)
        user.save()
        response = 0
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
