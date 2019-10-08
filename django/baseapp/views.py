from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from . import helpers


@login_required(redirect_field_name=None)
def main_view(request):
    try:
        context = helpers.get_baseapp_context(request)
    except Exception:
        helpers.view_exception(Exception)
        raise Http404("HTTP 404 Error")
    return render(request, "baseapp/main.html", context)


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
