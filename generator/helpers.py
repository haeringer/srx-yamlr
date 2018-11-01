from .models import *

import yaml


def importyaml(yamlfile):

    with open(yamlfile, 'r') as stream:
        configdata = yaml.load(stream)

    # import zones
    SrxZone.objects.all().delete()
    for zone in configdata['zones']:
        SrxZone.objects.update_or_create(zone_name=zone)

    # import addresses
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

    # import applications
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

    # import policies
    SrxPolicy.objects.all().delete()
    for p, v in configdata['policies'].items():

        obj, created = SrxPolicy.objects.update_or_create(policy_name=p)

        # manytomany fields cannot be populated with
        # update_or_create(), therefore use .add()
        frm = SrxZone.objects.get(zone_name=v['from'])
        obj.from_zone.add(frm)

        to = SrxZone.objects.get(zone_name=v['to'])
        obj.to_zone.add(to)

        src = v['src']
        if isinstance(src, list):
            for i in src:
                src = SrxAddress.objects.get(address_name=i)
                obj.source_address.add(src)
        else:
            src = SrxAddress.objects.get(address_name=src)
            obj.source_address.add(src)

        dest = v['dest']
        if isinstance(dest, list):
            for i in dest:
                dst = SrxAddress.objects.get(address_name=i)
                obj.destination_address.add(dst)
        else:
            dst = SrxAddress.objects.get(address_name=dest)
            obj.destination_address.add(dst)

        apps = v['apps']
        if isinstance(apps, list):
            for i in apps:
                app = SrxApplication.objects.get(application_name=i)
                obj.applications.add(app)
        else:
            app = SrxApplication.objects.get(application_name=apps)
            obj.applications.add(app)
