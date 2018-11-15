from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse
from .models import *
from .helpers import importyaml


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
    return render(request, 'generator/index.html', context)


def getaddressdata(request):
    objectid = request.GET.get('objectid', None)
    is_address = False

    try:
        obj = SrxAddress.objects.get(uuid=objectid)
        is_address = True
    except:
        obj = SrxAddrSet.objects.get(uuid=objectid)

    parentzone = SrxZone.objects.get(id=obj.zone_id)

    response_data = {}
    response_data['parentzone'] = parentzone.zone_name
    if is_address == True:
        response_data['obj_name'] = obj.address_name
        response_data['obj_val'] = obj.address_ip
    else:
        response_data['obj_name'] = obj.addrset_name
        response_data['obj_val'] = []
        for adr in obj.address.all():
            response_data['obj_val'].append(str(adr))

    return JsonResponse(response_data, safe=False)


def getapplicationdata(request):
    objectid = request.GET.get('objectid', None)
    is_application = False

    try:
        obj = SrxApplication.objects.get(uuid=objectid)
        is_application = True
    except:
        obj = SrxAppSet.objects.get(uuid=objectid)

    response_data = {}
    if is_application == True:
        protocol = SrxProtocol.objects.get(id=obj.protocol_id)
        response_data['obj_name'] = obj.application_name
        # response_data['obj_val'] = []
        # response_data['obj_val'].append(str(protocol.protocol_type))
        # response_data['obj_val'].append(str(obj.application_port))
        response_data['obj_port'] = obj.application_port
        response_data['obj_protocol'] = protocol.protocol_type
    else:
        response_data['obj_name'] = obj.applicationset_name
        response_data['obj_apps'] = []
        for app in obj.applications.all():
            response_data['obj_apps'].append(str(app))

    return JsonResponse(response_data, safe=False)

