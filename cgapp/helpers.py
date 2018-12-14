from .models import *

import oyaml as yaml
import json
import collections
def makehash():
    return collections.defaultdict(makehash)


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
            # retrieve zone object from zone model
            # to make foreign key connection
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

        # abuse try/except error handling for application logic
        # in order to keep things simple
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



def buildyaml(objdata, src, objtype, configid, action):

    # print(
    #     'objdata:', objdata,
    #     'src:', src,
    #     'objtype:', objtype,
    #     'configid:', configid,
    #     'action:', action,
    # )

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
    if src != 'newobj':
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
    elif src == 'app':
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
    validate zone logic
    '''
    if src == 'from':
        q = SrxZone.objects.filter(tozone__uuid=configid)
        if q:
            tozone = q[0].name
            if tozone == od_fromzone:
                return
        q = SrxZone.objects.filter(fromzone__uuid=configid)
        if q:
            fromzone = q[0].name
            if fromzone != od_fromzone:
                return
    elif src == 'to':
        q = SrxZone.objects.filter(fromzone__uuid=configid)
        if q:
            fromzone = q[0].name
            if fromzone == od_tozone:
                return
        q = SrxZone.objects.filter(tozone__uuid=configid)
        if q:
            tozone = q[0].name
            if tozone != od_tozone:
                return

    '''
    add or delete delivered object to/from created policy
    '''
    if action == 'add' and src != 'newobj':
        if od_fromzone:
            o = SrxZone.objects.get(name=od_fromzone)
            obj.fromzone.add(o)
        if od_tozone:
            o = SrxZone.objects.get(name=od_tozone)
            obj.tozone.add(o)
        if od_srcaddress:
            o = SrxAddress.objects.get(name=od_srcaddress)
            obj.srcaddress.add(o)
        if od_srcaddrset:
            o = SrxAddrSet.objects.get(name=od_srcaddrset)
            obj.srcaddrset.add(o)
        if od_destaddress:
            o = SrxAddress.objects.get(name=od_destaddress)
            obj.destaddress.add(o)
        if od_destaddrset:
            o = SrxAddrSet.objects.get(name=od_destaddrset)
            obj.destaddrset.add(o)
        if od_application:
            o = SrxApplication.objects.get(name=od_application)
            obj.application.add(o)
        if od_appset:
            o = SrxAppSet.objects.get(name=od_appset)
            obj.appset.add(o)
    if action == 'delete':
        # zones are not removed until last address object is deleted -
        # see database queries + filling yaml_variables below
        if od_srcaddress:
            o = SrxAddress.objects.get(name=od_srcaddress)
            obj.srcaddress.remove(o)
        if od_srcaddrset:
            o = SrxAddrSet.objects.get(name=od_srcaddrset)
            obj.srcaddrset.remove(o)
        if od_destaddress:
            o = SrxAddress.objects.get(name=od_destaddress)
            obj.destaddress.remove(o)
        if od_destaddrset:
            o = SrxAddrSet.objects.get(name=od_destaddrset)
            obj.destaddrset.remove(o)
        if od_application:
            o = SrxApplication.objects.get(name=od_application)
            obj.application.remove(o)
        if od_appset:
            o = SrxAppSet.objects.get(name=od_appset)
            obj.appset.remove(o)

    '''
    add newly created object
    '''
    if action == 'add' and src == 'newobj':
        if objtype == 'address':
            zone = SrxZone.objects.get(name=objdata['addresszone'])
            name = objdata['addressname']
            ip = objdata['addressip']
            SrxAddress.objects.create(zone=zone, name=name, ip=ip,
                                      uuid=configid)
        if objtype == 'addrset':
            zone = SrxZone.objects.get(name=objdata['addrsetzone'])
            name = objdata['addrsetname']
            addresses = objdata['addrsetobjects']
            obj = SrxAddrSet.objects.create(zone=zone, name=name,
                                            uuid=configid)
            for i in addresses:
                o = SrxAddress.objects.get(name=i)
                obj.addresses.add(o)


    '''
    query database for objects (existing and newly created ones) and assign
    values to yaml_variables
    '''
    ### SourceClass.objects.filter(m2mfield__m2mfield=value)
    # - the first field is the manytomanyfield of the referencing class
    #   (SrxPolicy in this case), of which we want to retrieve the value
    # - the second field is a m2mfield of the referencing class of which
    #   we know the value, so we can use it as a filter
    # - fields must have 'related_name'
    q = SrxZone.objects.filter(fromzone__uuid=configid)
    yaml_fromzone = od_fromzone if not q else q[0].name

    q = SrxZone.objects.filter(tozone__uuid=configid)
    yaml_tozone = od_tozone if not q else q[0].name


    q = SrxAddress.objects.filter(srcaddress__uuid=configid)
    srcaddress = queryset_to_var(q)

    q = SrxAddrSet.objects.filter(srcaddrset__uuid=configid)
    srcaddrset = queryset_to_var(q)

    if srcaddress and srcaddrset:
        if not isinstance(srcaddress, list): srcaddress = [srcaddress]
        if not isinstance(srcaddrset, list): srcaddrset = [srcaddrset]
        yaml_source = srcaddress + srcaddrset
    if srcaddress and not srcaddrset: yaml_source = srcaddress
    if srcaddrset and not srcaddress: yaml_source = srcaddrset
    if not srcaddress and not srcaddrset: yaml_source = ''

    if src == 'from' and action == 'delete' and not yaml_source:
        obj.fromzone.remove(SrxZone.objects.get(name=od_fromzone))
        yaml_fromzone = ''


    q = SrxAddress.objects.filter(destaddress__uuid=configid)
    destaddress = queryset_to_var(q)

    q = SrxAddrSet.objects.filter(destaddrset__uuid=configid)
    destaddrset = queryset_to_var(q)

    if destaddress and destaddrset:
        if not isinstance(destaddress, list): destaddress = [destaddress]
        if not isinstance(destaddrset, list): destaddrset = [destaddrset]
        yaml_destination = destaddress + destaddrset
    if destaddress and not destaddrset: yaml_destination = destaddress
    if destaddrset and not destaddress: yaml_destination = destaddrset
    if not destaddress and not destaddrset: yaml_destination = ''

    if src == 'to' and action == 'delete' and not yaml_destination:
        obj.tozone.remove(SrxZone.objects.get(name=od_tozone))
        yaml_tozone = ''


    q = SrxApplication.objects.filter(application__uuid=configid)
    application = queryset_to_var(q)

    q = SrxAppSet.objects.filter(appset__uuid=configid)
    appset = queryset_to_var(q)

    if application and appset:
        if not isinstance(application, list): application = [application]
        if not isinstance(appset, list): appset = [appset]
        yaml_applications = application + appset
    if application and not appset: yaml_applications = application
    if appset and not application: yaml_applications = appset
    if not application and not appset: yaml_applications = ''

    # query for newly created objects
    q = SrxAddress.objects.filter(uuid=configid)
    if q:
        # use collections.defaultdict to build nested dictionary
        defaultdict_newaddress = makehash()
        for i in q:
            addresszone = str(SrxZone.objects.get(id = i.zone_id))
            addressname = i.name
            addressip = i.ip

            # fill nested defaultdict with values
            defaultdict_newaddress[addresszone]['addresses'][
                addressname] = addressip

            # because yaml.dump cannot handle defaultdict,
            # convert it to standard dict via json library
            temp_jsondump = json.dumps(defaultdict_newaddress)
            yaml_newaddress = json.loads(temp_jsondump)
    else: yaml_newaddress = ''

    q = SrxAddrSet.objects.filter(uuid=configid)
    if q:
        defaultdict_newaddrset = makehash()
        for i in q:
            addrsetzone = str(SrxZone.objects.get(id = i.zone_id))
            addrsetname = i.name

            q_adr = SrxAddress.objects.filter(addresses__name=i.name)
            if len(q_adr) > 1:
                addrsetobjects = []
                for a in q_adr:
                    addrsetobjects.append(a.name)
            else: addrsetobjects = q_adr[0].name

            defaultdict_newaddrset[addrsetzone]['addrsets'][
                addrsetname] = addrsetobjects
            temp_jsondump = json.dumps(defaultdict_newaddrset)
            yaml_newaddrset = json.loads(temp_jsondump)
    else: yaml_newaddrset = ''

    # TODO application

    # TODO application set


    '''
    prepare dictionary with values from current config
    '''
    prep_policies = {}
    if yaml_fromzone:
        prep_policies.update({'fromzone': yaml_fromzone})
    if yaml_tozone:
        prep_policies.update({'tozone': yaml_tozone})
    if yaml_source:
        prep_policies.update({'source': yaml_source})
    if yaml_destination:
        prep_policies.update({'destination': yaml_destination})
    if yaml_applications:
        prep_policies.update({'applications': yaml_applications})

    '''
    build policy name and put prepared dict into parent
    '''
    if isinstance(yaml_source, list):
        source = yaml_source[0]+'-etc'
    else: source = yaml_source
    if isinstance(yaml_destination, list):
        destination = yaml_destination[0]+'-etc'
    else: destination = yaml_destination

    policyname = 'allow-' + source + '-to-' + destination

    SrxPolicy.objects.update_or_create(uuid=configid,
                                       defaults={'name': policyname})

    dict_yaml = {}
    if prep_policies:
        dict_yaml['policies'] = {
            policyname: prep_policies
        }
    if yaml_newaddress:
        dict_yaml.update({'zones': yaml_newaddress})
    if yaml_newaddrset:
        dict_yaml.update({'zones': yaml_newaddrset})

    '''
    dump dict into yaml file and into variable for return
    '''
    with open('config-new.yml', 'w') as outfile:
        yaml.dump(dict_yaml, outfile, default_flow_style=False)

    yamlconfig = yaml.dump(dict_yaml, default_flow_style=False)

    return yamlconfig



def queryset_to_var(queryset):
    if queryset:
        if len(queryset) > 1:
            rval = []
            for q in queryset:
                rval.append(q.name)
        else: rval = queryset[0].name
    else:
        rval = ''
    return rval