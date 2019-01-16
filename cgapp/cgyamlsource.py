from .models import *
import oyaml as yaml



class yamlSource:

    def __init__(self, sourcefile):
        with open(sourcefile, 'r') as infile:
            self.data = yaml.load(infile)

    def reset_db(self):
        SrxPolicy.objects.all().delete()
        SrxAppSet.objects.all().delete()
        SrxAddrSet.objects.all().delete()
        SrxApplication.objects.all().delete()
        SrxAddress.objects.all().delete()
        SrxProtocol.objects.all().delete()
        SrxZone.objects.all().delete()

    def import_zones(self):
        for zone in self.data['zones']:
            SrxZone.objects.update_or_create(name=zone)

    def import_addresses(self):
        for zone, values in self.data['zones'].items():
            address = values['addresses'] # {'HostOne': '10.1.1.1/32'}
            for name, ip in address.items():
                # retrieve zone object from zone model
                # to make foreign key connection
                srxzonename = SrxZone.objects.get(name=zone)
                SrxAddress.objects.update_or_create(
                    zone=srxzonename,
                    name=name,
                    ip=ip
                )

    def import_addrsets(self):
        for zone, values in self.data['zones'].items():
            if 'addrsets' in values:
                if values['addrsets']:
                    addrset = values['addrsets']
                    for setname, addrss in addrset.items():
                        srxzonename = SrxZone.objects.get(name=zone)
                        obj, created = SrxAddrSet.objects.update_or_create(
                            zone=srxzonename,
                            name=setname
                        )
                        if isinstance(addrss, list):
                            for i in addrss:
                                addr = SrxAddress.objects.get(name=i)
                                obj.addresses.add(addr)
                        else:
                            addr = SrxAddress.objects.get(name=addrss)
                            obj.addresses.add(addr)

    def import_protocols(self):
        for p in self.data['protocols']:
            SrxProtocol.objects.update_or_create(ptype=p)

    def import_applications(self):
        for app, values in self.data['applications'].items():
            port = values.get('port')
            protocol = values.get('protocol')
            srxprotocoltype = SrxProtocol.objects.get(ptype=protocol)
            SrxApplication.objects.update_or_create(
                name=app,
                protocol=srxprotocoltype,
                port=port
            )
        for app, values in self.data['default-applications'].items():
            protocol = values.get('protocol')
            srxprotocoltype = SrxProtocol.objects.get(ptype=protocol)
            if 'port' in values:
                port = values.get('port')
            else: port = ''
            SrxApplication.objects.update_or_create(
                name=app,
                protocol=srxprotocoltype,
                port=port
            )

    def import_appsets(self):
        for appset, values in self.data['applicationsets'].items():
            obj, created = SrxAppSet.objects.update_or_create(name=appset)
            if isinstance(values, list):
                for i in values:
                    app = SrxApplication.objects.get(name=i)
                    obj.applications.add(app)
            else:
                app = SrxApplication.objects.get(name=values)
                obj.applications.add(app)

    def import_policies(self):
        for policy, values in self.data['policies'].items():

            obj, created = SrxPolicy.objects.update_or_create(name=policy)

            frm = SrxZone.objects.get(name=values['fromzone'])
            to = SrxZone.objects.get(name=values['tozone'])
            src = values['source']
            dest = values['destination']
            apps = values['application']

            # manytomany fields cannot be populated with
            # update_or_create(), therefore use .add()
            obj.fromzone.add(frm)
            obj.tozone.add(to)

            # abuse try/except error handling for application logic
            # in order to keep things simple
            if isinstance(src, list):
                for i in src:
                    try: obj.srcaddress.add(SrxAddress.objects.get(name=i))
                    except: obj.srcaddrset.add(SrxAddrSet.objects.get(name=i))
            elif src != 'any':
                try: obj.srcaddress.add(SrxAddress.objects.get(name=src))
                except: obj.srcaddrset.add(SrxAddrSet.objects.get(name=src))
            else:
                q = SrxAddress.objects.filter(zone=frm).get(name='any')
                obj.srcaddress.add(q)

            if isinstance(dest, list):
                for i in dest:
                    try: obj.destaddress.add(SrxAddress.objects.get(name=i))
                    except: obj.destaddrset.add(SrxAddrSet.objects.get(name=i))
            elif dest != 'any':
                try: obj.destaddress.add(SrxAddress.objects.get(name=dest))
                except: obj.destaddrset.add(SrxAddrSet.objects.get(name=dest))
            else:
                q = SrxAddress.objects.filter(zone=to).get(name='any')
                obj.destaddress.add(q)

            if isinstance(apps, list):
                for i in apps:
                    try: obj.application.add(SrxApplication.objects.get(name=i))
                    except: obj.appset.add(SrxAppSet.objects.get(name=i))
            else:
                try: obj.application.add(SrxApplication.objects.get(name=apps))
                except: obj.appset.add(SrxAppSet.objects.get(name=apps))
