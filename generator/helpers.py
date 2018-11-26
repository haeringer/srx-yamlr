from .models import *

import oyaml as yaml


def importyaml(yamlfile):

    with open(yamlfile, 'r') as infile:
        configdata = yaml.load(infile)

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
    for appset, values in configdata['applicationsets'].items():
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

        frm = SrxZone.objects.get(zone_name=values['fromzone'])
        to = SrxZone.objects.get(zone_name=values['tozone'])
        src = values['source']
        dest = values['destination']
        apps = values['applications']

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


def buildyaml(objdata, src, configid):

    od_fromzone = ''
    od_source = ''
    od_tozone = ''
    od_destination = ''
    od_applications = ''

    # read object data delivered at function call
    if src == 'from':
        od_fromzone = objdata['parentzone']
        od_source = objdata['obj_name']
    elif src == 'to':
        od_tozone = objdata['parentzone']
        od_destination = objdata['obj_name']
    else:
        od_applications = objdata['obj_name']

    # create new config in database with current config id from frontend
    obj, created = SrxNewConfig.objects.update_or_create(configid=configid)

    # query database for config that has already been created
    cfg = SrxNewConfig.objects.filter(configid=configid)

    if cfg:
        # retrieve strings from queryset
        db_fromzone = cfg[0].fromzone
        db_tozone = cfg[0].tozone
        db_source = cfg[0].source
        db_destination = cfg[0].destination
        db_applications = cfg[0].applications

        # add new objects to empty fields or concatenate with existing objects
        fromzone = od_fromzone if not db_fromzone else db_fromzone
        tozone = od_tozone if not db_tozone else db_tozone

        if od_source and db_source:
            if not isinstance(db_source, list):
                print('is not list')
                source = [db_source, od_source]
                print(type(db_source))
            else:
                source = db_source.append(od_source)
        elif od_source and not db_source: source = od_source
        else: source = db_source

        if od_destination and db_destination:
            if db_destination[-1:] == ']':
                destination = db_destination[:-1]+','+od_destination+']'
            else:
                destination = '['+db_destination+','+od_destination+']'
        elif od_destination and not db_destination: destination = od_destination
        else: destination = db_destination

        if od_applications and db_applications:
            if db_applications[-1:] == ']':
                applications = db_applications[:-1]+','+od_applications+']'
            else:
                applications = '['+db_applications+','+od_applications+']'
        elif od_applications and not db_applications: applications = od_applications
        else: applications = db_applications

        # update objects in database
        obj, created = SrxNewConfig.objects.update_or_create(
            configid=configid,
            defaults={
                'configid': configid,
                'fromzone': fromzone,
                'tozone': tozone,
                'source': source,
                'destination': destination,
                'applications': applications,
            }
        )

    # prepare new dictionary with values from current config
    policy_prep = dict(
        policyname_dummy = dict(
            fromzone = fromzone,
            tozone = tozone,
            source = source,
            destination = destination,
            applications = applications,
        )
    )
    # build policy name and swap prepared key with actual name
    # policyname = 'allow-' + source + '-to-' + destination
    policyname = 'policyname_temp'
    policy_prep[policyname] = policy_prep.pop('policyname_dummy')
    # put prepared policy into final policies dict
    dict_yaml = {}
    dict_yaml['policies'] = policy_prep

    # dump dict into yaml file
    with open('config-new.yml', 'w') as outfile:
        newconfig = yaml.dump(dict_yaml, outfile, default_flow_style=False)

    return 'return config in yaml format here'