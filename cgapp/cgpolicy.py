from .models import SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxZone, SrxPolicy


class newPolicy:

    def __init__(self):
        self.policymodel_obj = None
        self.policyid = None

    def update_or_create_policy(self, policyid, configid):
        '''Update or create new policy in database with configid & policyid'''

        obj, created = SrxPolicy.objects.update_or_create(policyid=policyid,
                                                          configid=configid)
        self.policymodel_obj = obj
        self.policyid = policyid

    def validate_zone_logic(self, srxobj):

        pid = self.policyid

        if srxobj.src == 'from':
            # query tozone m2m-field of SrxPolicy model with current policyid
            q = SrxZone.objects.filter(tozone__policyid=pid)
            if q:
                tozone = q[0].name
                if tozone == srxobj.parentzone:
                    return 1
            # query fromzone m2m-field of SrxPolicy model with current policyid
            q = SrxZone.objects.filter(fromzone__policyid=pid)
            if q:
                fromzone = q[0].name
                if fromzone != srxobj.parentzone:
                    return 1
        elif srxobj.src == 'to':
            q = SrxZone.objects.filter(fromzone__policyid=pid)
            if q:
                fromzone = q[0].name
                if fromzone == srxobj.parentzone:
                    return 1
            q = SrxZone.objects.filter(tozone__policyid=pid)
            if q:
                tozone = q[0].name
                if tozone != srxobj.parentzone:
                    return 1
        return 1

    def add_object(self, s):
        '''add delivered SrxObject (s) to new policy'''

        p = self.policymodel_obj

        if s.srx_type == 'address' or s.srx_type == 'addrset':
            z = SrxZone.objects.get(name=s.parentzone)
            p.tozone.add(z) if s.src == 'to' else p.fromzone.add(z)

            if s.srx_type == 'address':
                o = SrxAddress.objects.filter(zone=z).get(name=s.name)
                p.destaddress.add(o) if s.src == 'to' else p.srcaddress.add(o)

            if s.srx_type == 'addrset':
                o = SrxAddrSet.objects.filter(zone=z).get(name=s.name)
                p.destaddrset.add(o) if s.src == 'to' else p.srcaddrset.add(o)

        if s.srx_type == 'application':
            o = SrxApplication.objects.get(name=s.name)
            p.application.add(o)

        if s.srx_type == 'appset':
            o = SrxAppSet.objects.get(name=s.name)
            p.appset.add(o)

    def delete_object(self, s):
        '''delete delivered SrxObject (s) from new policy (p)'''

        p = self.policymodel_obj

        if s.srx_type == 'address' or s.srx_type == 'addrset':
            z = SrxZone.objects.get(name=s.parentzone)

            if s.srx_type == 'address':
                o = SrxAddress.objects.filter(zone=z).get(name=s.name)
                p.destaddress.remove(o) if s.src == 'to' \
                    else p.srcaddress.remove(o)

            if s.srx_type == 'addrset':
                o = SrxAddrSet.objects.filter(zone=z).get(name=s.name)
                p.destaddrset.remove(o) if s.src == 'to' \
                    else p.srcaddrset.remove(o)

            # query address m2m-fields of SrxPolicy model with current policyid
            a = SrxAddress.objects.filter(srcaddress__policyid=p.policyid)
            b = SrxAddrSet.objects.filter(srcaddrset__policyid=p.policyid)
            if not a and not b:
                p.tozone.remove(z) if s.src == 'to' \
                    else p.fromzone.remove(z)

        if s.srx_type == 'application':
            o = SrxApplication.objects.get(name=s.name)
            p.application.remove(o)

        if s.srx_type == 'appset':
            o = SrxAppSet.objects.get(name=s.name)
            p.appset.remove(o)
