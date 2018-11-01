yamlfile = 'kami-test.yml'

from django.shortcuts import render

from .models import *

from .helpers import importyaml

# call function from helpers.py to import YAML data
importyaml(yamlfile)

def index(request):
    zones = SrxZone.objects.all()
    context = {'zones': zones}
    return render(request, 'generator/index.html', context)