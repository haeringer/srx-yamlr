import logging
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from copy import copy

from srxapp.utils import config, helpers, source

logger = logging.getLogger(__name__)


@login_required(redirect_field_name=None)
def mainView(request):
    try:
        sourcedict = copy(request.session['sourcedict'])
        context = {
            'zones': sourcedict['zones'],
            'addresses': sourcedict['addresses'],
            'addrsets': sourcedict['addrsets'],
            'applications': sourcedict['applications'],
            'appsets': sourcedict['appsets'],
            'username': request.user.username,
        }
    except Exception:
        logger.error(helpers.view_exception(Exception))
        raise Http404("HTTP 404 Error")
    return render(request, 'srxapp/main.html', context)


@login_required(redirect_field_name=None)
def load_objects(request):
    try:
        # Initialize empty dictionaries for user session
        request.session['sourcedict'] = {}
        request.session['configdict'] = {}

        helpers.git_clone_to_workspace()

        logger.info('Importing YAML source data...')
        src = source.sourceData(request)
        src.import_zones()
        src.import_addresses()
        src.import_addrsets()
        src.import_applications()
        src.import_appsets()
        src.import_policies()

        response = {}
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_add_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        configdict = srxpolicy.add_address()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        configdict = srxpolicy.delete_address()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_add_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        configdict = srxpolicy.add_application()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        configdict = srxpolicy.delete_application()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_address(request):
    try:
        srxobject = config.srxObject(request)
        configdict = srxobject.create_address()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_addrset(request):
    try:
        srxobject = config.srxObject(request)
        configdict = srxobject.create_addrset()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_application(request):
    try:
        srxobject = config.srxObject(request)
        configdict = srxobject.create_application()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_appset(request):
    try:
        srxobject = config.srxObject(request)
        configdict = srxobject.create_appset()
        request.session['configdict'] = configdict
        response = helpers.convert_dict_to_yaml(configdict)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def filter_objects(request):
    selectedzone = request.GET.get('selectedzone', None)
    if selectedzone == 'Choose Zone...':
        return JsonResponse(None, safe=False)

    sourcedict = copy(request.session['sourcedict'])

    addresses_filtered = []
    for address in sourcedict['addresses']:
        if address['zone'] == selectedzone:
            addresses_filtered.append(address['name'])

    response = dict(addresses=addresses_filtered)
    return JsonResponse(response, safe=False)


def get_yamlconfig(request):
    response = helpers.convert_dict_to_yaml(request.session['configdict'])
    return JsonResponse(response, safe=False)


def set_token_gogs(request):
    try:
        user = User.objects.get(username=request.user.username)
        user.usersettings.gogs_tkn = request.POST.get('token', None)
        user.save()
        response = dict(return_value=0)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
