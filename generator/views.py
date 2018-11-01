from django.shortcuts import render

from .models import *

from .helpers import importyaml


yamlfile = 'kami-test.yml'

# call function from helpers.py to import YAML data
try:
    importyaml(yamlfile)
except:
    print('YAML import failed')

def index(request):
    zones = SrxZone.objects.all()
    context = {'zones': zones}
    return render(request, 'generator/index.html', context)