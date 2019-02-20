import logging
from copy import copy

from cgapp.models import SrxZone, SrxAddress, SrxAddrSet, SrxProtocol, \
                            SrxApplication, SrxAppSet

logger = logging.getLogger(__name__)


class srxPolicy:

    def __init__(self, request):
        self.configdict = request.session['configdict']
        self.direction = request.POST.get('direction', None)
        self.name = request.POST.get('objname', None)
        self.zone = request.POST.get('zone', None)
        self.policyid = request.POST.get('policyid', None)
        self.policyname = 'allow-{0}-to-{0}'.format(self.policyid)

    def get_direction_variables(self):
        if self.direction == 'from':
            zone, direction = 'fromzone', 'source'
        elif self.direction == 'to':
            zone, direction = 'tozone', 'destination'
        return zone, direction

    def extract_policy_from_configdict(self):
        cd = copy(self.configdict)
        d = cd.setdefault('policies', {}).setdefault(self.policyname, {})
        return cd, d

    def update_configdict_with_policy(self, configdict, policydict):
        if policydict == {}:
            configdict['policies'].pop(self.policyname)
            if configdict['policies'] == {}:
                configdict.pop('policies')
        else:
            configdict['policies'][self.policyname].update(policydict)
        return configdict

    def add_address(self):
        cd, d = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        d[zone] = self.zone
        if direction not in d:
            d[direction] = self.name
        else:
            if isinstance(d[direction], str):
                d[direction] = [d[direction]]
            d[direction].append(self.name)

        return self.update_configdict_with_policy(cd, d)

    def delete_address(self):
        cd, d = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        if isinstance(d[direction], list):
            d[direction].remove(self.name)
            if len(d[direction]) == 1:
                d[direction] = d[direction][0]
        else:
            d.pop(direction)
            d.pop(zone)

        return self.update_configdict_with_policy(cd, d)

    def add_application(self):
        cd, d = self.extract_policy_from_configdict()

        if 'application' not in d:
            d['application'] = self.name
        else:
            if isinstance(d['application'], str):
                d['application'] = [d['application']]
            d['application'].append(self.name)

        return self.update_configdict_with_policy(cd, d)

    def delete_application(self):
        cd, d = self.extract_policy_from_configdict()

        if isinstance(d['application'], list):
            d['application'].remove(self.name)
            if len(d['application']) == 1:
                d['application'] = d['application'][0]
        else:
            d.pop('application')

        return self.update_configdict_with_policy(cd, d)


class srxObject:

    def __init__(self, request):
        self.configdict = request.session['configdict']
        self.name = request.POST.get('name', None)
        self.zone = request.POST.get('zone', None)
        self.protocol = request.POST.get('protocol', None)
        self.port = request.POST.get('port', None)
        self.value = request.POST.get('value', None)
        self.valuelist = request.POST.getlist('valuelist[]', None)

    def extract_zone_from_configdict(self):
        cd = copy(self.configdict)
        d = cd.setdefault('zones', {}).setdefault(self.zone, {})
        return cd, d

    def update_configdict_with_zone(self, configdict, zonedict):
        configdict['zones'][self.zone].update(zonedict)
        return configdict

    def create_address(self):
        zone = SrxZone.objects.get(name=self.zone)
        SrxAddress.objects.create(zone=zone, name=self.name, ip=self.value)

        cd, d = self.extract_zone_from_configdict()

        if 'addresses' not in d:
            d['addresses'] = {self.name: self.value}
        else:
            if isinstance(d['addresses'], dict):
                d['addresses'] = [d['addresses']]
            d['addresses'].append({self.name: self.value})

        return self.update_configdict_with_zone(cd, d)

    def create_addrset(self):
        zone = SrxZone.objects.get(name=self.zone)
        obj = SrxAddrSet.objects.create(zone=zone, name=self.name)
        for name in self.valuelist:
            address = SrxAddress.objects.get(name=name)
            obj.addresses.add(address)

        cd, d = self.extract_zone_from_configdict()

        if 'addrsets' not in d:
            d['addrsets'] = {self.name: self.valuelist}
        else:
            if isinstance(d['addrsets'], dict):
                d['addrsets'] = [d['addrsets']]
            d['addrsets'].append({self.name: self.valuelist})

        return self.update_configdict_with_zone(cd, d)

    def create_application(self):
        protocol = SrxProtocol.objects.get(ptype=self.protocol)
        SrxApplication.objects.create(name=self.name, protocol=protocol,
                                      port=self.port)

        cd = copy(self.configdict)
        d = cd.setdefault('applications', {})

        d[self.name] = {'protocol': self.protocol, 'port': self.port}

        cd['applications'].update(d)
        return cd

    def create_appset(self):
        obj = SrxAppSet.objects.create(name=self.name)
        for name in self.valuelist:
            application = SrxApplication.objects.get(name=name)
            obj.applications.add(application)

        cd = copy(self.configdict)
        d = cd.setdefault('applicationsets', {})

        d[self.name] = self.valuelist

        cd['applicationsets'].update(d)
        return cd
