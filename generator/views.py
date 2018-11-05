from django.shortcuts import render, get_list_or_404

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