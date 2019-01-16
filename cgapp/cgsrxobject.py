from .models import *



class srxObject:

    def __init__(self):
        self.objectid = None
        self.configid = None
        self.model = None
        self.src = None
        self.name = None
        self.srx_type = None
        self.address_type = None
        self.parentzone = None
        self.valuelist = None
        self.protocol = None
        self.value = None
        self.port = None
        self.apps = None


    def set_obj_values_http(self, r):
        '''Set object values that are included in http request'''

        self.objectid = r.POST.get('objectid', None)
        self.src = r.POST.get('source', None)


    def set_obj_values_db(self):
        '''Set additional object values by retrieving data from db'''

        # Search database for delivered object + determine srx object type
        #
        i = self.objectid
        s = self.src
        if s == 'from' or s == 'to':
            m = SrxAddress.objects.filter(id=i).first()
            if m:
                t = 'address'
                a = 'srcaddress' if s == 'from' else 'destaddress'
            else:
                m = SrxAddrSet.objects.filter(id=i).first()
                if m:
                    t = 'addrset'
                    a = 'srcaddrset' if s == 'from' else 'destaddrset'
            self.address_type = a
        elif s == 'app':
            m = SrxApplication.objects.filter(id=i).first()
            if m:
                t = 'application'
            else:
                m = SrxAppSet.objects.filter(id=i).first()
                if m:
                    t = 'appset'

        self.model = m
        self.name = m.name
        self.srx_type = t

        # Retrieve data correlating to object (e.g. zone) from db
        #
        if t == 'address' or t == 'addrset':
            parentzone = SrxZone.objects.get(id=m.zone_id)
            self.parentzone = parentzone.name

            if t == 'address':
                self.value = m.ip

            elif t == 'addrset':
                self.value = []
                for adr in m.addresses.all():
                    self.value.append(str(adr))

        elif t == 'application':
            protocol = SrxProtocol.objects.get(id=m.protocol_id)
            self.port = m.port
            self.protocol = protocol.ptype

        elif t == 'appset':
            self.apps = []
            for app in m.applications.all():
                self.apps.append(str(app))


    def set_obj_values_new(self, r, c):
        self.configid = c
        self.srx_type = r.POST.get('objtype', None)
        self.name = r.POST.get('name', None)
        self.value = r.POST.get('value', None)
        self.valuelist = r.POST.getlist('valuelist[]', None)
        self.parentzone = r.POST.get('zone', None)
        self.protocol = r.POST.get('protocol', None)
        self.port = r.POST.get('port', None)


    def save_new_obj(self):
        '''add newly created object to db'''

        o = self.srx_type
        n = self.name
        c = self.configid
        v = self.value
        l = self.valuelist
        p = self.port

        if o == 'address':
            z = SrxZone.objects.get(name=self.parentzone)
            SrxAddress.objects.create(zone=z, name=n, ip=v, configid=c)

        if o == 'addrset':
            z = SrxZone.objects.get(name=self.parentzone)
            obj = SrxAddrSet.objects.create(zone=z, name=n, configid=c)
            for i in l:
                a = SrxAddress.objects.get(name=i)
                obj.addresses.add(a)

        if o == 'application':
            pr = SrxProtocol.objects.get(ptype=self.protocol)
            SrxApplication.objects.create(name=n, protocol=pr,
                                          port=p, configid=c)

        if o == 'appset':
            obj = SrxAppSet.objects.create(name=n, configid=c)
            for i in l:
                a = SrxApplication.objects.get(name=i)
                obj.applications.add(a)
