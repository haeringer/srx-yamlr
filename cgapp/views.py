from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse
from .models import *
from .helpers import importyaml, buildyaml


yamlfile = 'kami-test.yml'

# call function from helpers.py to import YAML data
try:
    importyaml(yamlfile)
except Exception as e:
    print('YAML import failed because of the following error:')
    print(e)


def index(request):
    try:
        zones = get_list_or_404(SrxZone)
        addresses = get_list_or_404(SrxAddress)
        addrsets = get_list_or_404(SrxAddrSet)
        applications = get_list_or_404(SrxApplication)
        appsets = get_list_or_404(SrxAppSet)
        policies = get_list_or_404(SrxPolicy)
        context = {
            'zones': zones,
            'addresses': addresses,
            'addrsets': addrsets,
            'applications': applications,
            'appsets': appsets,
            'policies': policies
        }
    except:
        raise Http404("HTTP 404 Error")
    return render(request, 'cgapp/index.html', context)


def objectdata(request):
    objectid = request.GET.get('objectid', None)
    configid = request.GET.get('configid', None)
    src = None
    obj_type = ''

    obj = SrxAddress.objects.filter(uuid=objectid).first()
    if obj != None:
        obj_type = 'address'
    else:
        obj = SrxAddrSet.objects.filter(uuid=objectid).first()
        if obj != None:
            obj_type = 'addrset'
        else:
            obj = SrxApplication.objects.filter(uuid=objectid).first()
            if obj != None:
                obj_type = 'application'
            else:
                obj = SrxAppSet.objects.filter(uuid=objectid).first()
                if obj != None:
                    obj_type = 'appset'

    response_data = {}

    if obj_type == 'address' or obj_type == 'addrset':
        src = request.GET.get('source')
        parentzone = SrxZone.objects.get(id=obj.zone_id)
        response_data['parentzone'] = parentzone.zone_name

        if obj_type == 'address':
            response_data['obj_name'] = obj.address_name
            response_data['obj_val'] = obj.address_ip

        elif obj_type == 'addrset':
            response_data['obj_name'] = obj.addrset_name
            response_data['obj_val'] = []
            for adr in obj.address.all():
                response_data['obj_val'].append(str(adr))

    elif obj_type == 'application':
        protocol = SrxProtocol.objects.get(id=obj.protocol_id)
        response_data['obj_name'] = obj.application_name
        response_data['obj_port'] = obj.application_port
        response_data['obj_protocol'] = protocol.protocol_type

    elif obj_type == 'appset':
        response_data['obj_name'] = obj.applicationset_name
        response_data['obj_apps'] = []
        for app in obj.applications.all():
            response_data['obj_apps'].append(str(app))

    yaml = buildyaml(response_data, src, configid)
    print(yaml)

    return JsonResponse(response_data, safe=False)
