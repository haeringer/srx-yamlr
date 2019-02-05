from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import SrxZone, SrxAddress, SrxAddrSet, SrxApplication, SrxAppSet
import os
import traceback
import json

from .cgyamlsource import yamlSource
from .cgsrxobject import srxObject
from .cgpolicy import newPolicy
from .cgyamlconfig import yamlConfig
from .cghelpers import queryset_to_var


yamlconfig = None


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
        # Instantiate yamlConfig object with a new configid
        global yamlconfig
        yamlconfig = yamlConfig()
        print('Cfgen configid:', yamlconfig.configid)

    return render(request, 'cgapp/main.html', context)


def loadobjects(request):

    loadpolicies = request.GET.get('loadpolicies', None)
    response = {}

    try:
        ys = yamlSource(os.environ.get('CFGEN_YAMLFILE', ''))
        print('Cfgen importyaml (policies == {}) start'.format(loadpolicies))
        if loadpolicies == 'False':
            ys.reset_db()
            ys.import_zones()
            ys.import_addresses()
            ys.import_addrsets()
            ys.import_protocols()
            ys.import_applications()
            ys.import_appsets()
        if loadpolicies == 'True':
            ys.import_policies()
    except Exception:
        print('Cfgen YAML import failed because of the following error:')
        print(traceback.format_exc())
        response['error'] = json.dumps(traceback.format_exc())

    print('Cfgen importyaml (policies == {}) done'.format(loadpolicies))
    return JsonResponse(response, safe=False)


@csrf_exempt
def updatepolicy(request):

    a = request.POST.get('action', None)
    i = request.POST.get('policyid', None)
    y = yamlconfig
    c = y.configid
    response = {}

    try:
        # Instantiate object for srx object + set object values
        s = srxObject()
        s.set_obj_values_http(request)
        s.set_obj_values_db()

        # Instantiate policy object + create or update policy in db
        p = newPolicy()
        p.update_or_create_policy(i, c)
        print('Cfgen policyid:', i)

        if p.validate_zone_logic(s) == 0:
            response['error'] = 'Zone validation failed'

        # Add or delete srx object to/from policy
        if a == 'add':
            p.add_object(s)
        if a == 'delete':
            p.delete_object(s)

        # Update yamlConfig object
        y.set_yaml_values()
        y.set_yaml_config()

        # Set values for http response
        response['obj_name'] = s.name
        response['parentzone'] = s.parentzone
        response['obj_val'] = s.value
        response['obj_port'] = s.port
        response['obj_protocol'] = s.protocol
        response['obj_apps'] = s.apps

        response['yamlconfig'] = y.configuration

    except Exception:
        print('Cfgen Updating the policy failed because of following error:')
        print(traceback.format_exc())
        response['error'] = json.dumps(traceback.format_exc())

    return JsonResponse(response, safe=False)


@csrf_exempt
def newobject(request):

    y = yamlconfig
    c = y.configid
    response = {}

    try:
        # Instantiate object for srx object + set object values
        s = srxObject()
        s.set_obj_values_new(request, c)
        s.save_new_obj()

        # Update yamlConfig object
        y.set_yaml_values()
        y.set_yaml_config()

        response['yamlconfig'] = y.configuration

    except Exception:
        print('Cfgen Adding new object failed because of the following error:')
        print(traceback.format_exc())
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
    addresses = queryset_to_var(q)

    response = {}
    response['addresses'] = addresses

    return JsonResponse(response, safe=False)


def channelsView(request):
    return render(request, 'cgapp/modals.html', {})
