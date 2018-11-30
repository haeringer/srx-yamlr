from .models import *

import oyaml as yaml


def importyaml(yamlfile):

    with open(yamlfile, 'r') as infile:
        configdata = yaml.load(infile)

    # always populate protocol with tcp + udp
    SrxProtocol.objects.update_or_create(ptype='tcp')
    SrxProtocol.objects.update_or_create(ptype='udp')

    '''
    import zones
    '''
    SrxZone.objects.all().delete()
    for zone in configdata['zones']:
        SrxZone.objects.update_or_create(name=zone)

    '''
    import addresses
    '''
    SrxAddress.objects.all().delete()
    for zone, values in configdata['zones'].items():
        address = values['addresses'] # {'HostOne': '10.1.1.1/32'}
        for name, ip in address.items():
            # retrieve zone object from zone model to make foreign key connection
            srxzonename = SrxZone.objects.get(name=zone)
            SrxAddress.objects.update_or_create(
                zone=srxzonename,
                name=name,
                ip=ip
            )

    '''
    import address sets
    '''
    SrxAddrSet.objects.all().delete()
    for zone, values in configdata['zones'].items():
        if 'addrsets' in values:
            addrset = values['addrsets']
            for setname, addresses in addrset.items():
                srxzonename = SrxZone.objects.get(name=zone)
                obj, created = SrxAddrSet.objects.update_or_create(
                    zone=srxzonename,
                    name=setname
                )
                if isinstance(addresses, list):
                    for i in addresses:
                        addr = SrxAddress.objects.get(name=i)
                        obj.address.add(addr)
                else:
                    addr = SrxAddress.objects.get(name=addresses)
                    obj.address.add(addr)

    '''
    import applications
    '''
    SrxApplication.objects.all().delete()
    for app, values in configdata['applications'].items():
        port = values.get('port')
        protocol = values.get('protocol')
        srxprotocoltype = SrxProtocol.objects.get(ptype=protocol)
        SrxApplication.objects.update_or_create(
            name=app,
            protocol=srxprotocoltype,
            port=port
        )

    '''
    import application sets
    '''
    SrxAppSet.objects.all().delete()
    for appset, values in configdata['applicationsets'].items():
        obj, created = SrxAppSet.objects.update_or_create(name=appset)
        if isinstance(values, list):
            for i in values:
                app = SrxApplication.objects.get(name=i)
                obj.applications.add(app)
        else:
            app = SrxApplication.objects.get(name=values)
            obj.applications.add(app)


    '''
    import policies
    '''
    SrxPolicy.objects.all().delete()
    for policy, values in configdata['policies'].items():

        obj, created = SrxPolicy.objects.update_or_create(name=policy)

        frm = SrxZone.objects.get(name=values['fromzone'])
        to = SrxZone.objects.get(name=values['tozone'])
        src = values['source']
        dest = values['destination']
        apps = values['applications']

        # manytomany fields cannot be populated with
        # update_or_create(), therefore use .add()
        obj.fromzone.add(frm)
        obj.tozone.add(to)

        if isinstance(src, list):
            for i in src:
                try: obj.srcaddress.add(SrxAddress.objects.get(name=i))
                except: obj.srcaddrset.add(SrxAddrSet.objects.get(name=i))
        else:
            try: obj.srcaddress.add(SrxAddress.objects.get(name=src))
            except: obj.srcaddrset.add(SrxAddrSet.objects.get(name=src))

        if isinstance(dest, list):
            for i in dest:
                try: obj.destaddress.add(SrxAddress.objects.get(name=i))
                except: obj.destaddrset.add(SrxAddrSet.objects.get(name=i))
        else:
            try: obj.destaddress.add(SrxAddress.objects.get(name=dest))
            except: obj.destaddrset.add(SrxAddrSet.objects.get(name=dest))

        if isinstance(apps, list):
            for i in apps:
                try: obj.application.add(SrxApplication.objects.get(name=i))
                except: obj.appset.add(SrxAppSet.objects.get(name=i))
        else:
            try: obj.application.add(SrxApplication.objects.get(name=apps))
            except: obj.appset.add(SrxAppSet.objects.get(name=apps))


def buildyaml(objdata, src, objtype, configid):

    od_fromzone = ''
    od_tozone = ''
    od_srcaddress = ''
    od_srcaddrset = ''
    od_destaddress = ''
    od_destaddrset = ''
    od_application = ''
    od_appset = ''

    '''
    read object data delivered at function call
    '''
    n = objdata['obj_name']
    if src == 'from':
        od_fromzone = objdata['parentzone']
        if objtype == 'address':
            od_srcaddress = n
            objtype = 'srcaddress'
        else:
            od_srcaddrset = n
            objtype = 'srcaddrset'
    elif src == 'to':
        od_tozone = objdata['parentzone']
        if objtype == 'address':
            od_destaddress = n
            objtype = 'destaddress'
        else:
            od_destaddrset = n
            objtype = 'destaddrset'
    else:
        if objtype == 'application':
            od_application = n
            objtype = 'application'
        elif objtype == 'appset':
            od_appset = n
            objtype = 'appset'

    '''
    create new policy in database with current config id from frontend
    '''
    obj, created = SrxPolicy.objects.update_or_create(uuid=configid)

    '''
    add delivered object to created policy
    '''
    if od_fromzone != '':
        obj.fromzone.add(SrxZone.objects.get(name=od_fromzone))

    if od_tozone != '':
        obj.tozone.add(SrxZone.objects.get(name=od_tozone))

    if od_srcaddress != '':
        obj.srcaddress.add(SrxAddress.objects.get(name=od_srcaddress))

    if od_srcaddrset != '':
        obj.srcaddrset.add(SrxAddrSet.objects.get(name=od_srcaddrset))

    if od_destaddress != '':
        obj.destaddress.add(SrxAddress.objects.get(name=od_destaddress))

    if od_destaddrset != '':
        obj.destaddrset.add(SrxAddrSet.objects.get(name=od_destaddrset))

    if od_application != '':
        obj.application.add(SrxApplication.objects.get(name=od_application))

    if od_appset != '':
        obj.appset.add(SrxAppSet.objects.get(name=od_appset))


    '''
    query database for objects (existing and newly created ones) and assign
    values to yaml_variables
    '''
    ### SourceClass.objects.filter(m2mfield__m2mfield=value)
    ### - the first field is the manytomanyfield of the referencing
    ###   class, of which we want to retrieve the value
    ### - the second field is a m2mfield of the referencing class
    ###   of which we know the value, so we can use it as a filter
    q = SrxZone.objects.filter(fromzone__uuid=configid)
    yaml_fromzone = od_fromzone if not q else str(q[0])

    q = SrxZone.objects.filter(tozone__uuid=configid)
    yaml_tozone = od_tozone if not q else str(q[0])


    q = SrxAddress.objects.filter(srcaddress__uuid=configid)
    if q:
        if len(q) > 1:
            srcaddress = []
            for i in q:
                srcaddress.append(str(i))
        else: srcaddress = str(q[0])
    else: srcaddress = ''

    q = SrxAddrSet.objects.filter(srcaddrset__uuid=configid)
    if q:
        if len(q) > 1:
            srcaddrset = []
            for i in q:
                srcaddrset.append(str(i))
        else: srcaddrset = str(q[0])
    else: srcaddrset = ''

    if srcaddress and srcaddrset:
        if not isinstance(srcaddress, list): srcaddress = [srcaddress]
        if not isinstance(srcaddrset, list): srcaddrset = [srcaddrset]
        yaml_source = srcaddress + srcaddrset
    if srcaddress and not srcaddrset: yaml_source = srcaddress
    if srcaddrset and not srcaddress: yaml_source = srcaddrset
    if not srcaddress and not srcaddrset: yaml_source = ''


    q = SrxAddress.objects.filter(destaddress__uuid=configid)
    if q:
        if len(q) > 1:
            destaddress = []
            for i in q:
                destaddress.append(str(i))
        else: destaddress = str(q[0])
    else: destaddress = ''

    q = SrxAddrSet.objects.filter(destaddrset__uuid=configid)
    if q:
        if len(q) > 1:
            destaddrset = []
            for i in q:
                destaddrset.append(str(i))
        else: destaddrset = str(q[0])
    else: destaddrset = ''

    if destaddress and destaddrset:
        if not isinstance(destaddress, list): destaddress = [destaddress]
        if not isinstance(destaddrset, list): destaddrset = [destaddrset]
        yaml_destination = destaddress + destaddrset
    if destaddress and not destaddrset: yaml_destination = destaddress
    if destaddrset and not destaddress: yaml_destination = destaddrset
    if not destaddress and not destaddrset: yaml_destination = ''


    q = SrxApplication.objects.filter(application__uuid=configid)
    if q:
        if len(q) > 1:
            application = []
            for i in q:
                application.append(str(i))
        else: application = str(q[0])
    else: application = ''

    q = SrxAppSet.objects.filter(appset__uuid=configid)
    if q:
        if len(q) > 1:
            appset = []
            for i in q:
                appset.append(str(i))
        else: appset = str(q[0])
    else: appset = ''

    if application and appset:
        if not isinstance(application, list): application = [application]
        if not isinstance(appset, list): appset = [appset]
        yaml_applications = application + appset
    if application and not appset: yaml_applications = application
    if appset and not application: yaml_applications = appset
    if not application and not appset: yaml_applications = ''



    '''
    prepare dictionary with values from current config
    '''
    policy_prep = dict(
        policyname_dummy = dict(
            fromzone = yaml_fromzone,
            tozone = yaml_tozone,
            source = yaml_source,
            destination = yaml_destination,
            applications = yaml_applications,
        )
    )

    '''
    build policy name and swap prepared key with actual name
    '''
    source = ''.join(yaml_source)
    destination = ''.join(yaml_destination)
    policyname = 'allow-' + source + '-to-' + destination
    policy_prep[policyname] = policy_prep.pop('policyname_dummy')
    # put prepared policy into final policies dict
    dict_yaml = {}
    dict_yaml['policies'] = policy_prep

    SrxPolicy.objects.update_or_create(uuid=configid, defaults={'name': policyname})


    '''
    dump dict into yaml file
    '''
    with open('config-new.yml', 'w') as outfile:
        newconfig = yaml.dump(dict_yaml, outfile, default_flow_style=False)

    return 'return config in yaml format here'