from .models import SrxZone, SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxPolicy, SrxProtocol

import yaml


def importyaml(yamlfile):

    with open(yamlfile, 'r') as stream:
        configdata = yaml.load(stream)

    # import zones
    for zone in configdata['zones']:
        SrxZone.objects.update_or_create(
            zone_name=zone
        )

    # import addresses
    for zone, values in configdata['zones'].items():
        address = values['addresses'] # {'HostOne': '10.1.1.1/32'}
        for name, ip in address.items():
            # retrieve zone name from zone model to make foreign key connection
            srxzone_ = SrxZone.objects.get(zone_name=zone)
            SrxAddress.objects.update_or_create(
                zone=srxzone_, address_name=name, address_ip=ip
            )

    # import applications
    for app, values in configdata['applications'].items():
        port = values.get('port')
        protocol = values.get('protocol')
        protocol_ = SrxProtocol.objects.get(protocol_type=protocol)
        SrxApplication.objects.update_or_create(
            application_name=app, protocol=protocol_, application_port=port
        )

    # import policies
    # for policy, values in configdata['policies'].items():
        # frm = SrxZone.objects.get(zone_name=values.get('from'))
        # to = SrxZone.objects.get(zone_name=values.get('to'))
        # src = SrxAddress.objects.get(address_name=values.get('src'))
        # dest = SrxAddress.objects.get(address_name=values.get('dest'))
        # apps = SrxApplication.objects.get(application_name=values.get('apps'))
        # SrxPolicy.objects.update_or_create(
        #     policy_name=policy, from_zone=frm, to_zone=to, source_address=src,
        #     destination_address=dest, applications=apps
        # )
        # obj, created = SrxPolicy.objects.update_or_create(policy_name=policy)
        # if obj.to_zone:
        # # if hasattr(obj, 'to_zone'):
        #     bla = 'egal'
        # else:
        #     obj.to_zone.add(to)


        # try:
        #     bla = obj.objects.get(to_zone)
        #     obj.to_zone.add(to)
        # except obj.to_zone.exis