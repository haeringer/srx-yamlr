from copy import deepcopy
from uuid import uuid4
from srxapp.utils import helpers


class srxPolicy:

    def __init__(self, request):
        self.configdict = request.session['configdict']
        self.sourcedict = request.session['sourcedict']
        self.direction = request.POST.get('direction', None)
        self.name = request.POST.get('objname', None)
        self.zone = request.POST.get('zone', None)
        self.policyname = request.POST.get('policyname', None)
        self.previousname = request.POST.get('previousname', None)

    def get_direction_variables(self):
        if self.direction == 'from':
            zone, direction = 'fromzone', 'source'
        elif self.direction == 'to':
            zone, direction = 'tozone', 'destination'
        return zone, direction

    def extract_policy_from_configdict(self):
        policydict = deepcopy(self.configdict.setdefault(
            'policies', {}).setdefault(self.policyname, {}))
        return policydict

    def update_configdict_with_policy(self, policydict):
        configdict = deepcopy(self.configdict)
        configdict.setdefault('policies', {}).setdefault(self.policyname, {})

        if policydict != {}:
            policy = {self.policyname: policydict}
            configdict['policies'].update(policy)
        else:
            configdict['policies'].pop(self.policyname)
            if configdict['policies'] == {}:
                configdict.pop('policies')

        helpers.log_config(configdict)
        return configdict

    def check_for_policy_existing(self, policydict):
        existing = False

        if 'source' not in policydict or 'destination' not in policydict:
            return

        sorted_dict_for_hash = helpers.dict_with_sorted_list_values(
            source=policydict['source'], destination=policydict['destination'])
        newpolicyhash = hash(repr(sorted_dict_for_hash))

        for policy in self.sourcedict['policies']:
            if newpolicyhash == policy['policyhash']:
                existing = True

        return existing

    def update_policyname(self):
        cd = self.configdict
        cd['policies'][self.policyname] = cd['policies'].pop(self.previousname)
        return cd

    def add_address(self):
        p = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        p[zone] = self.zone
        if direction not in p:
            p[direction] = self.name
        else:
            if isinstance(p[direction], str):
                p[direction] = [p[direction]]
            p[direction].append(self.name)

        existing = self.check_for_policy_existing(p)
        if existing:
            return 'policy_exists'

        return self.update_configdict_with_policy(p)

    def delete_address(self):
        p = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        if isinstance(p[direction], list):
            p[direction].remove(self.name)
            if len(p[direction]) == 1:
                p[direction] = p[direction][0]
        else:
            p.pop(direction)
            p.pop(zone)

        return self.update_configdict_with_policy(p)

    def add_application(self):
        p = self.extract_policy_from_configdict()

        if 'application' not in p:
            p['application'] = self.name
        else:
            if isinstance(p['application'], str):
                p['application'] = [p['application']]
            p['application'].append(self.name)

        return self.update_configdict_with_policy(p)

    def delete_application(self):
        p = self.extract_policy_from_configdict()

        if isinstance(p['application'], list):
            p['application'].remove(self.name)
            if len(p['application']) == 1:
                p['application'] = p['application'][0]
        else:
            p.pop('application')

        return self.update_configdict_with_policy(p)


class srxObject:

    def __init__(self, request):
        self.configdict = request.session['configdict']
        self.sourcedict = request.session['sourcedict']
        self.name = request.POST.get('name', None)
        self.zone = request.POST.get('zone', None)
        self.protocol = request.POST.get('protocol', None)
        self.port = request.POST.get('port', None)
        self.value = request.POST.get('value', None)
        self.valuelist = request.POST.getlist('valuelist[]', None)

    def extract_zone_from_configdict(self):
        zonedict = deepcopy(self.configdict.setdefault(
            'zones', {}).setdefault(self.zone, {}))
        return zonedict

    def update_configdict_with_zone(self, zonedict):
        configdict = deepcopy(self.configdict)
        configdict.setdefault('zones', {}).setdefault(self.zone, {})
        configdict['zones'][self.zone].update(zonedict)
        helpers.log_config(configdict)
        return configdict

    def create_address(self):
        self.sourcedict['addresses'].append({
            'name': self.name,
            'val': self.value,
            'zone': self.zone,
            'id': uuid4().hex,
        })

        z = self.extract_zone_from_configdict()

        if 'addresses' not in z:
            z['addresses'] = {self.name: self.value}
        else:
            if isinstance(z['addresses'], dict):
                z['addresses'] = [z['addresses']]
            z['addresses'].append({self.name: self.value})

        return self.update_configdict_with_zone(z)

    def create_addrset(self):
        self.sourcedict['addrsets'].append({
            'name': self.name,
            'val': self.valuelist,
            'zone': self.zone,
            'id': uuid4().hex,
        })

        z = self.extract_zone_from_configdict()

        if 'addrsets' not in z:
            z['addrsets'] = {self.name: self.valuelist}
        else:
            if isinstance(z['addrsets'], dict):
                z['addrsets'] = [z['addrsets']]
            z['addrsets'].append({self.name: self.valuelist})

        return self.update_configdict_with_zone(z)

    def create_application(self):
        val = str(self.protocol)+' '+str(self.port)

        self.sourcedict['applications'].append({
            'name': self.name,
            'val': val,
            'id': uuid4().hex,
        })

        configdict = dict(self.configdict)
        a = configdict.setdefault('applications', {})
        a[self.name] = {'protocol': self.protocol, 'port': self.port}
        configdict['applications'].update(a)

        helpers.log_config(configdict)
        return configdict

    def create_appset(self):
        self.sourcedict['appsets'].append({
            'name': self.name,
            'val': self.valuelist,
            'id': uuid4().hex,
        })

        configdict = dict(self.configdict)
        a = configdict.setdefault('applicationsets', {})
        a[self.name] = self.valuelist
        configdict['applicationsets'].update(a)

        helpers.log_config(configdict)
        return configdict
