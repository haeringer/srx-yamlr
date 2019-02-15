import json
import oyaml as yaml
import collections
import logging

from cgapp import cghelpers
from cgapp.models import SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxZone, SrxPolicy, SrxProtocol

logger = logging.getLogger(__name__)


def makehash():
    return collections.defaultdict(makehash)


def queryset_to_var(queryset):
    '''
    Convert django queryset to string or list, depending on queryset content
    '''

    if queryset:
        if len(queryset) > 1:
            rval = []
            for q in queryset:
                rval.append(q.name)
        else:
            rval = queryset[0].name
    else:
        rval = ''
    return rval


class srxPolicy:

    def __init__(self, request):
        self.configdict = request.session['configdict']
        self.objectid = request.POST.get('objectid', None)
        self.direction = request.POST.get('direction', None)
        self.policyid = request.POST.get('policyid', None)
        self.policyname = 'allow-{0}-to-{0}'.format(self.policyid)

    def add_address(self):
        cd = self.configdict

        obj = SrxAddress.objects.filter(id=self.objectid).first()
        if not obj:
            obj = SrxAddrSet.objects.filter(id=self.objectid).first()

        d = extract_from_nested_dict(cd, {})

        if self.direction == 'from':
            zone = 'fromzone'
            direction = 'source'
        elif self.direction == 'to':
            zone = 'tozone'
            direction = 'destination'

        d[zone] = str(obj.zone)
        if direction not in d:
            d[direction] = obj.name
        elif isinstance(d[direction], list):
            d[direction].append(obj.name)
        else:
            valuelist = [d[direction]]
            valuelist.append(obj.name)
            d[direction] = valuelist

        cd.setdefault('policies', {}).setdefault(self.policyname, {}).update(d)

        return cd

    def add_application(self):
        cd = self.configdict

        obj = SrxApplication.objects.filter(id=self.objectid).first()
        if not obj:
            obj = SrxAppSet.objects.filter(id=self.objectid).first()

        d = extract_from_nested_dict(self.configdict, {})

        if 'application' not in d:
            d['application'] = obj.name
        elif isinstance(d['application'], list):
            d['application'].append(obj.name)
        else:
            valuelist = [d['application']]
            valuelist.append(obj.name)
            d['application'] = valuelist

        cd.setdefault('policies', {}).setdefault(self.policyname, {}).update(d)

        return cd


def extract_from_nested_dict(nested_sourcedict, unnested_newdict):
    '''
    Extract a standard dict with only key/value pairs from a nested dict
    '''
    for key, value in nested_sourcedict.items():
        if isinstance(value, dict):
            extract_from_nested_dict(value, unnested_newdict)
        else:
            unnested_newdict[key] = value
    return unnested_newdict


def build_configdict(configid):
    '''query database for objects (existing and newly created ones) and
    assign values to configdict'''

    c = configid
    configdict = {}

    # SourceClass.objects.filter(m2mfield__m2mfield=value)
    # - first field = manytomanyfield of referencing class (SrxPolicy in
    #   this case) from which to get a value
    # - second field = manytomanyfield of referencing class of which the
    #   value is known, so it can be used as filter
    # - fields must have 'related_name'
    q = SrxZone.objects.filter(fromzone__configid=c)
    if q:
        yaml_fromzone = q[0].name
    else:
        yaml_fromzone = ''

    q = SrxZone.objects.filter(tozone__configid=c)
    if q:
        yaml_tozone = q[0].name
    else:
        yaml_tozone = ''

    q = SrxAddress.objects.filter(srcaddress__configid=c)
    srcaddress = cghelpers.queryset_to_var(q)

    q = SrxAddrSet.objects.filter(srcaddrset__configid=c)
    srcaddrset = cghelpers.queryset_to_var(q)

    if srcaddress and srcaddrset:
        if not isinstance(srcaddress, list):
            srcaddress = [srcaddress]
        if not isinstance(srcaddrset, list):
            srcaddrset = [srcaddrset]
        yaml_source = srcaddress + srcaddrset
    if srcaddress and not srcaddrset:
        yaml_source = srcaddress
    if srcaddrset and not srcaddress:
        yaml_source = srcaddrset
    if not srcaddress and not srcaddrset:
        yaml_source = ''

    q = SrxAddress.objects.filter(destaddress__configid=c)
    destaddress = cghelpers.queryset_to_var(q)

    q = SrxAddrSet.objects.filter(destaddrset__configid=c)
    destaddrset = cghelpers.queryset_to_var(q)

    if destaddress and destaddrset:
        if not isinstance(destaddress, list):
            destaddress = [destaddress]
        if not isinstance(destaddrset, list):
            destaddrset = [destaddrset]
        yaml_destination = destaddress + destaddrset
    if destaddress and not destaddrset:
        yaml_destination = destaddress
    if destaddrset and not destaddress:
        yaml_destination = destaddrset
    if not destaddress and not destaddrset:
        yaml_destination = ''

    q = SrxApplication.objects.filter(application__configid=c)
    application = cghelpers.queryset_to_var(q)

    q = SrxAppSet.objects.filter(appset__configid=c)
    appset = cghelpers.queryset_to_var(q)

    if application and appset:
        if not isinstance(application, list):
            application = [application]
        if not isinstance(appset, list):
            appset = [appset]
        yaml_applications = application + appset
    if application and not appset:
        yaml_applications = application
    if appset and not application:
        yaml_applications = appset
    if not application and not appset:
        yaml_applications = ''

    # query for newly created objects
    q = SrxAddress.objects.filter(configid=c)
    if q:
        # use collections.defaultdict to build nested dictionary
        defaultdict_newaddress = makehash()
        for i in q:
            addresszone = str(SrxZone.objects.get(id=i.zone_id))
            addressname = i.name
            addressip = i.ip

            # fill nested defaultdict with values
            defaultdict_newaddress[addresszone]['addresses'][
                                    addressname] = addressip

            # because yaml.dump cannot handle defaultdict,
            # convert it to standard dict via json library
            temp_jsondump = json.dumps(defaultdict_newaddress)
            yaml_newaddress = json.loads(temp_jsondump)
        logger.info('yaml_newaddress: {}'.format(yaml_newaddress))
    else:
        yaml_newaddress = ''

    q = SrxAddrSet.objects.filter(configid=c)
    if q:
        defaultdict_newaddrset = makehash()
        for i in q:
            addrsetzone = str(SrxZone.objects.get(id=i.zone_id))
            addrsetname = i.name
            q_adr = SrxAddress.objects.filter(addresses__name=i.name)
            if len(q_adr) > 1:
                addrsetobjects = []
                for a in q_adr:
                    addrsetobjects.append(a.name)
            else:
                addrsetobjects = q_adr[0].name

            defaultdict_newaddrset[addrsetzone]['addrsets'][
                                    addrsetname] = addrsetobjects
            temp_jsondump = json.dumps(defaultdict_newaddrset)
            yaml_newaddrset = json.loads(temp_jsondump)
        logger.info('yaml_newaddrset: {}'.format(yaml_newaddrset))
    else:
        yaml_newaddrset = ''

    q = SrxApplication.objects.filter(configid=c)
    if q:
        yaml_newapp = {}
        for i in q:
            appname = i.name
            appport = i.port
            appprotocol = str(SrxProtocol.objects.get(id=i.protocol_id))

            yaml_newapp.update({
                appname: {'protocol': appprotocol, 'port': appport}
            })
    else:
        yaml_newapp = ''

    q = SrxAppSet.objects.filter(configid=c)
    if q:
        yaml_newappset = {}
        for i in q:
            appsetname = i.name
            q_app = SrxApplication.objects.filter(
                applications__name=i.name)
            appsetobjects = cghelpers.queryset_to_var(q_app)

            yaml_newappset.update({appsetname: appsetobjects})
    else:
        yaml_newappset = ''

    '''
    prepare dictionary with values from current policy
    '''
    policy = {}
    if yaml_fromzone:
        policy.update({'fromzone': yaml_fromzone})
    if yaml_tozone:
        policy.update({'tozone': yaml_tozone})
    if yaml_source:
        policy.update({'source': yaml_source})
    if yaml_destination:
        policy.update({'destination': yaml_destination})
    if yaml_applications:
        policy.update({'applications': yaml_applications})

    '''
    build policy name and put prepared dict into parent
    '''
    if policy:
        if isinstance(yaml_source, list):
            source = yaml_source[0]+'-etc'
        else:
            source = yaml_source
        if isinstance(yaml_destination, list):
            destination = yaml_destination[0]+'-etc'
        else:
            destination = yaml_destination

        policyname = 'allow-' + source + '-to-' + destination

        SrxPolicy.objects.update_or_create(configid=c,
                                           defaults={'name': policyname})

    if policy:
        configdict['policies'] = {
            policyname: policy
        }
        logger.info('policy: {}'.format(policy))
    if yaml_newaddress and not yaml_newaddrset:
        configdict.update({'zones': yaml_newaddress})
    if yaml_newaddrset and not yaml_newaddress:
        configdict.update({'zones': yaml_newaddrset})
    if yaml_newaddress and yaml_newaddrset:
        # TODO: Bug: keys are overwritten in some combinations; use
        # defaultdict ?
        zone = next(iter(yaml_newaddress))
        zone2 = next(iter(yaml_newaddrset))
        if zone == zone2:
            adr_merged = {**yaml_newaddress[zone], **yaml_newaddrset[zone]}
            configdict.update({'zones': {zone: adr_merged}})
        else:
            adr_merged = {**yaml_newaddress, **yaml_newaddrset}
            configdict.update({'zones': adr_merged})
    if yaml_newapp:
        configdict.update({'applications': yaml_newapp})
    if yaml_newappset:
        configdict.update({'applicationsets': yaml_newappset})

    return configdict


def convert_to_yaml(configdict):
    '''dump configdict to yaml'''

    logger.info('configdict: {}'.format(configdict))
    yamlconfig = yaml.dump(configdict, default_flow_style=False)

    return yamlconfig
