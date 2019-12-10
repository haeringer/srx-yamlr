from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

from baseapp import helpers


@login_required(redirect_field_name=None)
def main_view(request):
    try:
        context = helpers.get_baseapp_context(request)
    except Exception:
        helpers.view_exception(Exception)
        raise Http404("HTTP 404 Error")
    return render(request, "srxpolsrch/main.html", context)
