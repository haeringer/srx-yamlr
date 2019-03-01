import logging
from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from srxapp.utils import config, helpers, source
from srxapp.models import SrxZone, SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet

logger = logging.getLogger(__name__)


@login_required(redirect_field_name=None)
def mainView(request):

    try:
        zones = get_list_or_404(SrxZone)
        addresses = get_list_or_404(SrxAddress)
        addrsets = get_list_or_404(SrxAddrSet)
        applications = get_list_or_404(SrxApplication)
        appsets = get_list_or_404(SrxAppSet)
        user = request.user.username
        context = {
            'zones': zones,
            'addresses': addresses,
            'addrsets': addrsets,
            'applications': applications,
            'appsets': appsets,
            'user': user,
        }
    except Exception:
        raise Http404("HTTP 404 Error")

    return render(request, 'srxapp/main.html', context)


def load_objects(request):
    try:
        loadpolicies = request.GET.get('loadpolicies', None)
        response = {}
        src = source.data()

        if loadpolicies == 'False':
            # Initialize empty configdict for user session
            request.session['configdict'] = {}

            helpers.git_clone_to_workspace()

            logger.info('Importyaml (policies={}) start'.format(loadpolicies))
            src.reset_db()
            src.import_zones()
            src.import_addresses()
            src.import_addrsets()
            src.import_protocols()
            src.import_applications()
            src.import_appsets()

        if loadpolicies == 'True':
            src.import_policies()

        logger.info('Importyaml (policies={}) done'.format(loadpolicies))

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

    if selectedzone != 'Choose Zone...':
        q = SrxZone.objects.filter(name=selectedzone)
        zone_id = q[0].id
    else:
        return JsonResponse(None, safe=False)

    q = SrxAddress.objects.filter(zone_id=zone_id)
    addresses = helpers.queryset_to_var(q)
    response = dict(addresses=addresses)
    return JsonResponse(response, safe=False)


def get_yamlconfig(request):
    response = helpers.convert_dict_to_yaml(request.session['configdict'])
    return JsonResponse(response, safe=False)
