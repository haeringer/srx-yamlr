import os
import oyaml as yaml

from cgapp.models import SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxZone, SrxPolicy, SrxProtocol


class data:

    def __init__(self):
        sourcefile = os.environ.get('CFGEN_YAMLFILE', '')

        with open(sourcefile, 'r') as infile:
            self.dataset = yaml.load(infile)

    def reset_db(self):
        SrxPolicy.objects.all().delete()
        SrxAppSet.objects.all().delete()
        SrxAddrSet.objects.all().delete()
        SrxApplication.objects.all().delete()
        SrxAddress.objects.all().delete()
        SrxProtocol.objects.all().delete()
        SrxZone.objects.all().delete()

    def import_zones(self):
        for zone in self.dataset['zones']:
            SrxZone.objects.update_or_create(name=zone)

    def import_addresses(self):
        for zone, values in self.dataset['zones'].items():
            z = SrxZone.objects.get(name=zone)
            # add 'any' zone to configuration
            SrxAddress.objects.update_or_create(zone=z, name='any', ip=z)
            a = values['addresses']  # {'HostOne': '10.1.1.1/32'}
            for name, ip in a.items():
                # retrieve zone object from zone model
                # to make foreign key connection
                SrxAddress.objects.update_or_create(zone=z, name=name, ip=ip)

    def import_addrsets(self):
        for zone, values in self.dataset['zones'].items():
            z = SrxZone.objects.get(name=zone)
            if 'addrsets' in values:
                if values['addrsets']:
                    a = values['addrsets']
                    for setname, addrss in a.items():
                        obj, created = SrxAddrSet.objects.update_or_create(
                            zone=z, name=setname
                        )
                        if isinstance(addrss, list):
                            for i in addrss:
                                addr = SrxAddress.objects.get(name=i)
                                obj.addresses.add(addr)
                        else:
                            addr = SrxAddress.objects.get(name=addrss)
                            obj.addresses.add(addr)

    def import_protocols(self):
        for p in self.dataset['protocols']:
            SrxProtocol.objects.update_or_create(ptype=p)

    def import_applications(self):
        for app, values in self.dataset['applications'].items():
            port = values.get('port')
            protocol = values.get('protocol')
            t = SrxProtocol.objects.get(ptype=protocol)
            SrxApplication.objects.update_or_create(name=app, protocol=t,
                                                    port=port)
        for app, values in self.dataset['default-applications'].items():
            protocol = values.get('protocol')
            t = SrxProtocol.objects.get(ptype=protocol)
            if 'port' in values:
                port = values.get('port')
            else:
                port = ''
            SrxApplication.objects.update_or_create(name=app, protocol=t,
                                                    port=port)

    def import_appsets(self):
        for appset, values in self.dataset['applicationsets'].items():
            obj, created = SrxAppSet.objects.update_or_create(name=appset)
            if isinstance(values, list):
                for i in values:
                    app = SrxApplication.objects.get(name=i)
                    obj.applications.add(app)
            else:
                app = SrxApplication.objects.get(name=values)
                obj.applications.add(app)

    def import_policies(self):
        for policy, values in self.dataset['policies'].items():

            obj, created = SrxPolicy.objects.update_or_create(name=policy)

            frm = SrxZone.objects.get(name=values['fromzone'])
            to = SrxZone.objects.get(name=values['tozone'])
            src = values['source']
            dest = values['destination']
            apps = values['application']

            obj.fromzone.add(frm)
            obj.tozone.add(to)

            if isinstance(src, list):
                for i in src:
                    in_address = SrxAddress.objects.filter(name=i)
                    if in_address:
                        obj.srcaddress.add(SrxAddress.objects.get(name=i))
                    else:
                        obj.srcaddrset.add(SrxAddrSet.objects.get(name=i))
            elif src != 'any':
                in_address = SrxAddress.objects.filter(name=src)
                if in_address:
                    obj.srcaddress.add(SrxAddress.objects.get(name=src))
                else:
                    obj.srcaddrset.add(SrxAddrSet.objects.get(name=src))
            else:
                q = SrxAddress.objects.filter(zone=frm).get(name='any')
                obj.srcaddress.add(q)

            if isinstance(dest, list):
                for i in dest:
                    in_address = SrxAddress.objects.filter(name=i)
                    if in_address:
                        obj.destaddress.add(SrxAddress.objects.get(name=i))
                    else:
                        obj.destaddrset.add(SrxAddrSet.objects.get(name=i))
            elif dest != 'any':
                in_address = SrxAddress.objects.filter(name=dest)
                if in_address:
                    obj.destaddress.add(SrxAddress.objects.get(name=dest))
                else:
                    obj.destaddrset.add(SrxAddrSet.objects.get(name=dest))
            else:
                q = SrxAddress.objects.filter(zone=to).get(name='any')
                obj.destaddress.add(q)

            if isinstance(apps, list):
                for i in apps:
                    in_application = SrxApplication.objects.filter(name=i)
                    if in_application:
                        obj.application.add(SrxApplication.objects.get(name=i))
                    else:
                        obj.appset.add(SrxAppSet.objects.get(name=i))
            else:
                in_application = SrxApplication.objects.filter(name=apps)
                if in_application:
                    obj.application.add(SrxApplication.objects.get(name=apps))
                else:
                    obj.appset.add(SrxAppSet.objects.get(name=apps))
