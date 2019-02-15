import os
import uuid
import git
import traceback
import json
import logging
import oyaml as yaml
from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from cgapp import cgsource, cghelpers
from cgapp.models import SrxZone, SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxPolicy, SrxProtocol

logger = logging.getLogger(__name__)


@login_required(redirect_field_name=None)
def mainView(request):

    param = request.GET.get('param', None)

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

    if param != 'reloadforms':

        request.session['configdict'] = {}
        request.session['configid'] = str(uuid.uuid4())
        logger.info('Configuration ID: {}'.format(request.session['configid']))

    return render(request, 'cgapp/main.html', context)


def loadobjects(request):

    loadpolicies = request.GET.get('loadpolicies', None)
    git_url = os.environ.get('CFGEN_GIT_URL', '')
    response = {}

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
        s = cgsource.data()
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
        logger.error('YAML import failed because of the following error:')
        logger.error(traceback.format_exc())
        response['error'] = json.dumps(traceback.format_exc())

    logger.info('Importyaml (policies == {}) done'.format(loadpolicies))
    return JsonResponse(response, safe=False)


def add_address_to_policy(request):
    policy = cghelpers.srxPolicy(request)
    configdict = policy.add_address()
    request.session['configdict'] = configdict
    response = dict(yamlconfig=yaml.dump(configdict, default_flow_style=False))
    return JsonResponse(response, safe=False)


def add_application_to_policy(request):
    policy = cghelpers.srxPolicy(request)
    configdict = policy.add_application()
    request.session['configdict'] = configdict
    response = dict(yamlconfig=yaml.dump(configdict, default_flow_style=False))
    return JsonResponse(response, safe=False)


def updatepolicy(request):

    action = request.POST.get('action', None)
    policyid = request.POST.get('policyid', None)
    objectid = request.POST.get('objectid', None)
    objtype = request.POST.get('objtype', None)
    source = request.POST.get('source', None)

    configid = request.session['configid']
    response = {}

    try:
        policy, created = SrxPolicy.objects.update_or_create(policyid=policyid,
                                                             configid=configid)
        logger.info('Cfgen policyid: {}'.format(policyid))

        if objtype == 'address' or objtype == 'addrset':

            if objtype == 'address':
                model = policy.update_address(objectid, source, action)
                response['obj_val'] = model.ip

            elif objtype == 'addrset':
                model = policy.update_addrset(objectid, source, action)
                response['obj_val'] = []
                for adr in model.addresses.all():
                    response['obj_val'].append(str(adr))

            policy.update_zone(model, source, action)
            response['parentzone'] = str(model.zone)

        elif objtype == 'application':
            model = policy.update_application(objectid, action)
            response['obj_port'] = model.port
            response['obj_protocol'] = str(model.protocol)

        elif objtype == 'appset':
            model = policy.update_appset(objectid, action)
            response['obj_apps'] = []
            for app in model.applications.all():
                response['obj_apps'].append(str(app))

        response['obj_name'] = str(model)

        # Call helper functions to build config and convert to yaml
        configdict = cghelpers.build_configdict(configid)
        yamlconfig = cghelpers.convert_to_yaml(configdict)

        request.session['yamlconfig'] = yamlconfig
        response['yamlconfig'] = yamlconfig

    except Exception:
        logger.error('Updating the policy failed because of following error:')
        logger.error(traceback.format_exc())
        response['error'] = json.dumps(traceback.format_exc())

    return JsonResponse(response, safe=False)


def newobject(request):

    objtype = request.POST.get('objtype', None)
    valuelist = request.POST.getlist('valuelist[]', None)
    protocol = request.POST.get('protocol', None)
    zone = request.POST.get('zone', None)
    n = request.POST.get('name', None)
    v = request.POST.get('value', None)
    p = request.POST.get('port', None)

    c = request.session['configid']
    response = {}

    try:
        if objtype == 'address':
            z = SrxZone.objects.get(name=zone)
            SrxAddress.objects.create(zone=z, name=n, ip=v, configid=c)

        elif objtype == 'addrset':
            z = SrxZone.objects.get(name=zone)
            obj = SrxAddrSet.objects.create(zone=z, name=n, configid=c)
            for i in valuelist:
                a = SrxAddress.objects.get(name=i)
                obj.addresses.add(a)

        elif objtype == 'application':
            pr = SrxProtocol.objects.get(ptype=protocol)
            SrxApplication.objects.create(name=n, protocol=pr,
                                          port=p, configid=c)

        elif objtype == 'appset':
            obj = SrxAppSet.objects.create(name=n, configid=c)
            for i in valuelist:
                a = SrxApplication.objects.get(name=i)
                obj.applications.add(a)

        # Call helper functions to build config and convert to yaml
        configdict = cghelpers.build_configdict(c)
        yamlconfig = cghelpers.convert_to_yaml(configdict)

        request.session['yamlconfig'] = yamlconfig
        response['yamlconfig'] = yamlconfig

    except Exception:
        logger.error('Creating object failed because of the following error:')
        logger.error(traceback.format_exc())
        response['error'] = json.dumps(traceback.format_exc())

    return JsonResponse(response, safe=False)


def filterobjects(request):

    selectedzone = request.GET.get('selectedzone', None)

    if selectedzone != 'Choose Zone...':
        q = SrxZone.objects.filter(name=selectedzone)
        zone_id = q[0].id
    else:
        return JsonResponse(None, safe=False)

    q = SrxAddress.objects.filter(zone_id=zone_id)
    addresses = cghelpers.queryset_to_var(q)

    response = {}
    response['addresses'] = addresses

    return JsonResponse(response, safe=False)
