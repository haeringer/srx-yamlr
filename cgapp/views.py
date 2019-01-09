from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import *
from .helpers import *
from .process import runansible
import sys, traceback, json


yamlfile = 'kami-kaze.yml'


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
    except:
        raise Http404("HTTP 404 Error")

    return render(request, 'cgapp/main.html', context)



def loadobjects(request):
    loadpolicies = request.GET.get('loadpolicies', 'False')
    print('importyaml start;', 'loadpolicies:', loadpolicies)
    response_data = {}

    try:
        conf = yamlConf(yamlfile)
        if loadpolicies == 'False':
            conf.importzones()
            conf.importaddresses()
            conf.importaddrsets()
            conf.importprotocols()
            conf.importapplications()
            conf.importappsets()
        elif loadpolicies == 'True':
            conf.importpolicies()
    except Exception as e:
        print('YAML import failed because of the following error:')
        print(traceback.format_exc())
        response_data['error'] = json.dumps(traceback.format_exc())

    print('importyaml done')
    return JsonResponse(response_data, safe=False)



@csrf_exempt
def objectdata(request):
    objectid = request.POST.get('objectid', None)
    configid = request.POST.get('configid', None)
    action = request.POST.get('action', None)
    src = request.POST.get('source', None)

    '''
    Search database for delivered object + determine object type
    '''
    if src == 'from' or src == 'to':
        obj = SrxAddress.objects.filter(id=objectid).first()
        if obj: objtype = 'address'
        else:
            obj = SrxAddrSet.objects.filter(id=objectid).first()
            if obj: objtype = 'addrset'
    elif src == 'app':
        obj = SrxApplication.objects.filter(id=objectid).first()
        if obj: objtype = 'application'
        else:
            obj = SrxAppSet.objects.filter(id=objectid).first()
            if obj: objtype = 'appset'

    '''
    Retrieve correlating data for object and put it into JSON response
    '''
    response_data = {}
    response_data['obj_name'] = obj.name

    if objtype == 'address' or objtype == 'addrset':
        parentzone = SrxZone.objects.get(id=obj.zone_id)
        response_data['parentzone'] = parentzone.name

        if objtype == 'address':
            response_data['obj_val'] = obj.ip

        elif objtype == 'addrset':
            response_data['obj_val'] = []
            for adr in obj.addresses.all():
                response_data['obj_val'].append(str(adr))

    elif objtype == 'application':
        protocol = SrxProtocol.objects.get(id=obj.protocol_id)
        response_data['obj_port'] = obj.port
        response_data['obj_protocol'] = protocol.ptype

    elif objtype == 'appset':
        response_data['obj_apps'] = []
        for app in obj.applications.all():
            response_data['obj_apps'].append(str(app))


    try:
        yaml = buildyaml(response_data, src, objtype, configid, action)
        response_data['yamlconfig'] = yaml
    except Exception as e:
        print('YAML build failed because of the following error:')
        print(traceback.format_exc())
        response_data['error'] = json.dumps(traceback.format_exc())


    return JsonResponse(response_data, safe=False)



@csrf_exempt
def newobject(request):
    configid = request.POST.get('configid', None)
    objtype = request.POST.get('objtype', None)
    objnew = {}
    objnew['addresszone'] = request.POST.get('addresszone', None)
    objnew['addressname'] = request.POST.get('addressname', None)
    objnew['addressip'] = request.POST.get('addressip', None)
    objnew['addrsetzone'] = request.POST.get('addrsetzone', None)
    objnew['addrsetname'] = request.POST.get('addrsetname', None)
    objnew['addrsetobjects'] = request.POST.getlist('addrsetobjects[]', None)
    objnew['appname'] = request.POST.get('appname', None)
    objnew['appport'] = request.POST.get('appport', None)
    objnew['appprotocol'] = request.POST.get('appprotocol', None)
    objnew['appsetname'] = request.POST.get('appsetname', None)
    objnew['appsetobjects'] = request.POST.getlist('appsetobjects[]', None)


    try:
        yaml = buildyaml(objnew, 'newobj', objtype, configid, 'add')
        response_data = {}
        response_data['yamlconfig'] = yaml
    except Exception as e:
        print('YAML build failed because of the following error:')
        print(e)

    return JsonResponse(response_data, safe=False)



def filterobjects(request):
    selectedzone = request.GET.get('selectedzone', None)

    if selectedzone != 'Choose Zone...':
        q = SrxZone.objects.filter(name=selectedzone)
        zone_id = q[0].id
    else:
        return JsonResponse(None, safe=False)

    q = SrxAddress.objects.filter(zone_id=zone_id)
    addresses = queryset_to_var(q)

    response_data = {}
    response_data['addresses'] = addresses

    return JsonResponse(response_data, safe=False)



@csrf_exempt
def checkconfig(request):


    runansible()

    response_data = {}
    response_data['output'] = 'bla'

    return JsonResponse(response_data, safe=False)