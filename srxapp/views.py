import os
import git
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
        context = {
            'zones': zones,
            'addresses': addresses,
            'addrsets': addrsets,
            'applications': applications,
            'appsets': appsets,
        }
    except Exception:
        raise Http404("HTTP 404 Error")

    return render(request, 'srxapp/main.html', context)


def load_objects(request):

    loadpolicies = request.GET.get('loadpolicies', None)
    git_url = os.environ.get('YAMLOMAT_GIT_URL', '')
    response = {}

    request.session['configdict'] = {}

    if loadpolicies == 'False':
        # abuse try/except for logic because git.Repo does not
        # provide proper return values if it doesn't succeed
        try:
            repo = git.Repo('workspace')
        except Exception:
            repo = None

        if repo:
            logger.info('Updating repo...')
            remote_repo = repo.remotes.origin
            remote_repo.pull()
        else:
            logger.info('Cloning repo...')
            git.Repo.clone_from(git_url, 'workspace')

    try:
        s = source.data()
        logger.info('Importyaml (policies == {}) start'.format(loadpolicies))
        if loadpolicies == 'False':
            s.reset_db()
            s.import_zones()
            s.import_addresses()
            s.import_addrsets()
            s.import_protocols()
            s.import_applications()
            s.import_appsets()
        if loadpolicies == 'True':
            s.import_policies()
    except Exception:
        response = helpers.view_exception(Exception)

    logger.info('Importyaml (policies == {}) done'.format(loadpolicies))
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
