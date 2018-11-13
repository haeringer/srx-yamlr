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
        applications = get_list_or_404(SrxApplication)
        policies = get_list_or_404(SrxPolicy)
        context = {
            'zones': zones,
            'addresses': addresses,
            'applications': applications,
            'policies': policies
        }
    except:
        raise Http404("HTTP 404 Error")
    return render(request, 'generator/index.html', context)


def getparentzone(request):
    objectid = request.GET.get('objectid', None)

    obj = SrxAddress.objects.get(uuid=objectid)
    parentzone = SrxZone.objects.get(id=obj.zone_id)

    response_data = {}
    response_data['obj_name'] = obj.address_name
    response_data['obj_ip'] = obj.address_ip
    response_data['parentzone'] = parentzone.zone_name

    return JsonResponse(response_data, safe=False)


def getapplicationdata(request):
    objectid = request.GET.get('objectid', None)

    obj = SrxApplication.objects.get(uuid=objectid)
    protocol = SrxProtocol.objects.get(id=obj.protocol_id)

    response_data = {}
    response_data['obj_name'] = obj.application_name
    response_data['obj_port'] = obj.application_port
    response_data['obj_protocol'] = protocol.protocol_type

    return JsonResponse(response_data, safe=False)

