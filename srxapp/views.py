import logging
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from copy import deepcopy

from srxapp.utils import config, helpers, source

logger = logging.getLogger(__name__)


@login_required(redirect_field_name=None)
def load_objects(request):
    try:
        # Initialize empty dictionaries for user session
        request.session['workingdict'] = {}
        request.session['configdict'] = {}
        request.session['pe_detail'] = {}

        helpers.git_clone_to_workspace()

        logger.info('Importing YAML source data...')
        src = source.sourceData(request)
        src.read_source_file()
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


@login_required(redirect_field_name=None)
def main_view(request):
    try:
        user = User.objects.get(username=request.user.username)
        token_set = helpers.check_if_token_set(user)
        workingdict = deepcopy(request.session['workingdict'])
        context = {
            'zones': workingdict['zones'],
            'addresses': workingdict['addresses'],
            'addrsets': workingdict['addrsets'],
            'applications': workingdict['applications'],
            'appsets': workingdict['appsets'],
            'username': request.user.username,
            'token_set': token_set,
        }
    except Exception:
        logger.error(helpers.view_exception(Exception))
        raise Http404("HTTP 404 Error")
    return render(request, 'srxapp/main.html', context)


def policy_add_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.add_address()
        if 'p_exists' not in result:
            request.session['configdict'] = result
            response = helpers.convert_dict_to_yaml(result)
        else:
            request.session['configdict'] = result['p_existing']
            request.session['pe_detail'] = result['pe_detail']
            response = 'p_exists'
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_address(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.delete_address()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_add_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.add_application()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_delete_application(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.delete_application()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_address(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_address()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_addrset(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_addrset()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_application(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_application()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def object_create_appset(request):
    try:
        srxobject = config.srxObject(request)
        result = srxobject.create_appset()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def policy_rename(request):
    try:
        srxpolicy = config.srxPolicy(request)
        result = srxpolicy.update_policyname()
        request.session['configdict'] = result
        response = helpers.convert_dict_to_yaml(result)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def filter_objects(request):
    selectedzone = request.GET.get('selectedzone', None)
    if selectedzone == 'Choose Zone...':
        return JsonResponse(None, safe=False)

    workingdict = deepcopy(request.session['workingdict'])

    addresses_filtered = []
    for address in workingdict['addresses']:
        if address['zone'] == selectedzone:
            addresses_filtered.append(address['name'])

    response = dict(addresses=addresses_filtered)
    return JsonResponse(response, safe=False)


def write_yamlconfig(request):
    try:
        logger.info('Writing YAML config to source file...')
        src = source.sourceData(request)
        src.update_source_file()
        response = helpers.git_get_diff()
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def get_yamlconfig(request):
    response = helpers.convert_dict_to_yaml(request.session['configdict'])
    return JsonResponse(response, safe=False)


def get_existing_policy_details(request):
    response = request.session['pe_detail']
    return JsonResponse(response, safe=False)


def set_token_gogs(request):
    try:
        user = User.objects.get(username=request.user.username)
        token = request.POST.get('token', None)
        token_encrypted = helpers.encrypt_string(token)
        user.usersettings.gogs_tkn = token_encrypted
        user.save()
        response = dict(return_value=0)
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
