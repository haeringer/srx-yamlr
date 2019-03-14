import os
import oyaml as yaml

from uuid import uuid4
from srxapp.utils import helpers


class sourceData:

    def __init__(self, request):
        self.sourcedict = request.session['sourcedict']
        sourcefile = os.environ.get('YM_YAMLFILE', '')
        with open(sourcefile, 'r') as infile:
            self.dataset = yaml.load(infile)

    def import_zones(self):
        zones = self.sourcedict.setdefault('zones', [])

        for name in self.dataset['zones']:
            zones.append({'name': name})

    def import_addresses(self):
        addresses = self.sourcedict.setdefault('addresses', [])

        for zone, values in self.dataset['zones'].items():
            zone_addresses = values['addresses']
            for name, ip in zone_addresses.items():
                addresses.append({
                    'name': name,
                    'val': ip,
                    'zone': zone,
                    'id': uuid4().hex,
                })
            # add one 'any' address per zone to configuration set
            addresses.append({
                'name': 'any',
                'val': zone,
                'zone': zone,
                'id': uuid4().hex,
            })

    def import_addrsets(self):
        addrsets = self.sourcedict.setdefault('addrsets', [])

        for zone, values in self.dataset['zones'].items():
            if 'addrsets' in values:
                if values['addrsets']:
                    for name, addresses in values['addrsets'].items():
                        addrsets.append({
                            'name': name,
                            'val': addresses,
                            'zone': zone,
                            'id': uuid4().hex,
                        })

    def import_applications(self):
        applications = self.sourcedict.setdefault('applications', [])

        def fill_application_list(applications_dict):
            for name, values in applications_dict.items():
                val = str(values['protocol'])+' '+str(values.get('port', ''))
                applications.append({
                    'name': name,
                    'val': val,
                    'id': uuid4().hex,
                })

        fill_application_list(self.dataset['applications'])
        fill_application_list(self.dataset['default-applications'])

    def import_appsets(self):
        appsets = self.sourcedict.setdefault('appsets', [])

        for name, values in self.dataset['applicationsets'].items():
            appsets.append({
                'name': name,
                'val': values,
                'id': uuid4().hex,
            })

    def import_policies(self):
        policies = self.sourcedict.setdefault('policies', [])

        for name, values in self.dataset['policies'].items():

            sorted_dict_for_hash = helpers.dict_with_sorted_list_values(
                source=values['source'], destination=values['destination'])
            policyhash = hash(repr(sorted_dict_for_hash))

            policies.append({
                'name': name,
                'policyhash': policyhash,
                'fromzone': values['fromzone'],
                'tozone': values['tozone'],
                'source': values['source'],
                'destination': values['destination'],
                'application': values['application'],
            })
