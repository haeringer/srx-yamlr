from .models import *

import yaml


def importyaml(yamlfile):

    with open(yamlfile, 'r') as stream:
        configdata = yaml.load(stream)

    # always populate protocol with tcp + udp
    SrxProtocol.objects.update_or_create(protocol_type='tcp')
    SrxProtocol.objects.update_or_create(protocol_type='udp')

    '''
    import zones
    '''
    SrxZone.objects.all().delete()
    for zone in configdata['zones']:
        SrxZone.objects.update_or_create(zone_name=zone)

    '''
    import addresses
    '''
    SrxAddress.objects.all().delete()
    for zone, values in configdata['zones'].items():
        address = values['addresses'] # {'HostOne': '10.1.1.1/32'}
        for name, ip in address.items():
            # retrieve zone object from zone model to make foreign key connection
            srxzone_ = SrxZone.objects.get(zone_name=zone)
            SrxAddress.objects.update_or_create(
                zone=srxzone_,
                address_name=name,
                address_ip=ip
            )

    '''
    import address sets
    '''
    SrxAddrSet.objects.all().delete()
    for zone, values in configdata['zones'].items():
        if 'addrsets' in values:
            addrset = values['addrsets']
            for setname, addresses in addrset.items():
                srxzone_ = SrxZone.objects.get(zone_name=zone)
                obj, created = SrxAddrSet.objects.update_or_create(
                    zone=srxzone_,
                    addrset_name=setname
                )
                if isinstance(addresses, list):
                    for i in addresses:
                        addr = SrxAddress.objects.get(address_name=i)
                        obj.address.add(addr)
                else:
                    addr = SrxAddress.objects.get(address_name=addresses)
                    obj.address.add(addr)

    '''
    import applications
    '''
    SrxApplication.objects.all().delete()
    for app, values in configdata['applications'].items():
        port = values.get('port')
        protocol = values.get('protocol')
        protocol_ = SrxProtocol.objects.get(protocol_type=protocol)
        SrxApplication.objects.update_or_create(
            application_name=app,
            protocol=protocol_,
            application_port=port
        )

    '''
    import application sets
    '''
    SrxAppSet.objects.all().delete()
    for appset, values in configdata['appsets'].items():
        obj, created = SrxAppSet.objects.update_or_create(applicationset_name=appset)
        if isinstance(values, list):
            for i in values:
                app = SrxApplication.objects.get(application_name=i)
                obj.applications.add(app)
        else:
            app = SrxApplication.objects.get(application_name=values)
            obj.applications.add(app)


    '''
    import policies
    '''
    SrxPolicy.objects.all().delete()
    for policy, values in configdata['policies'].items():

        obj, created = SrxPolicy.objects.update_or_create(policy_name=policy)

        frm = SrxZone.objects.get(zone_name=values['from'])
        to = SrxZone.objects.get(zone_name=values['to'])
        src = values['src']
        dest = values['dest']
        apps = values['apps']

        # manytomany fields cannot be populated with
        # update_or_create(), therefore use .add()
        obj.from_zone.add(frm)
        obj.to_zone.add(to)

        if isinstance(src, list):
            for i in src:
                try: obj.source_address.add(SrxAddress.objects.get(address_name=i))
                except: obj.source_addrset.add(SrxAddrSet.objects.get(addrset_name=i))
        else:
            try: obj.source_address.add(SrxAddress.objects.get(address_name=src))
            except: obj.source_addrset.add(SrxAddrSet.objects.get(addrset_name=src))

        if isinstance(dest, list):
            for i in dest:
                try: obj.destination_address.add(SrxAddress.objects.get(address_name=i))
                except: obj.destination_addrset.add(SrxAddrSet.objects.get(addrset_name=i))
        else:
            try: obj.destination_address.add(SrxAddress.objects.get(address_name=dest))
            except: obj.destination_addrset.add(SrxAddrSet.objects.get(addrset_name=dest))

        if isinstance(apps, list):
            for i in apps:
                try: obj.applications.add(SrxApplication.objects.get(application_name=i))
                except: obj.appsets.add(SrxAppSet.objects.get(applicationset_name=i))
        else:
            try: obj.applications.add(SrxApplication.objects.get(application_name=apps))
            except: obj.appsets.add(SrxAppSet.objects.get(applicationset_name=apps))
