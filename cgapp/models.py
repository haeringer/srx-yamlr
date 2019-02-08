from django.db import models


class BaseModel(models.Model):

    class Meta:
        abstract = True
        app_label = 'cgapp'


class SrxZone(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SrxAddress(BaseModel):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)
    configid = models.CharField(max_length=36, default=0)

    def __str__(self):
        return self.name


class SrxAddrSet(BaseModel):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    configid = models.CharField(max_length=36, default=0)
    addresses = models.ManyToManyField(SrxAddress, related_name='addresses')

    def __str__(self):
        return self.name


class SrxProtocol(BaseModel):
    ptype = models.CharField(max_length=12)

    def __str__(self):
        return self.ptype


class SrxApplication(BaseModel):
    name = models.CharField(max_length=255)
    protocol = models.ForeignKey(SrxProtocol, on_delete=models.CASCADE,
                                 default=0)
    configid = models.CharField(max_length=36, default=0)
    port = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class SrxAppSet(BaseModel):
    name = models.CharField(max_length=255)
    applications = models.ManyToManyField(SrxApplication,
                                          related_name='applications')
    configid = models.CharField(max_length=36, default=0)

    def __str__(self):
        return self.name


class SrxPolicy(BaseModel):

    name = models.CharField(max_length=255)
    fromzone = models.ManyToManyField(SrxZone, related_name='fromzone')
    tozone = models.ManyToManyField(SrxZone, related_name='tozone')
    srcaddress = models.ManyToManyField(SrxAddress, related_name='srcaddress')
    srcaddrset = models.ManyToManyField(SrxAddrSet, related_name='srcaddrset')
    destaddress = models.ManyToManyField(SrxAddress,
                                         related_name='destaddress')
    destaddrset = models.ManyToManyField(SrxAddrSet,
                                         related_name='destaddrset')
    application = models.ManyToManyField(SrxApplication,
                                         related_name='application')
    appset = models.ManyToManyField(SrxAppSet, related_name='appset')
    policyid = models.CharField(max_length=36, default=0)
    configid = models.CharField(max_length=36, default=0)

    def __str__(self):
        return self.name

    def update_address(self, objectid, src, action):
        obj = SrxAddress.objects.filter(id=objectid).first()

        if action == 'add':
            if src == 'from':
                self.srcaddress.add(obj)
            elif src == 'to':
                self.destaddress.add(obj)

        elif action == 'delete':
            if src == 'from':
                self.srcaddress.remove(obj)
            elif src == 'to':
                self.destaddress.remove(obj)

        return obj

    def update_addrset(self, objectid, src, action):
        obj = SrxAddrSet.objects.filter(id=objectid).first()

        if action == 'add':
            if src == 'from':
                self.srcaddrset.add(obj)
            elif src == 'to':
                self.destaddrset.add(obj)

        elif action == 'delete':
            if src == 'from':
                self.srcaddrset.remove(obj)
            elif src == 'to':
                self.destaddrset.remove(obj)

        return obj

    def update_zone(self, obj, src, action):

        if action == 'add':
            if src == 'from':
                self.fromzone.add(obj.zone)
            elif src == 'to':
                self.tozone.add(obj.zone)

        elif action == 'delete':
            if src == 'from':
                # query address m2m-fields of SrxPolicy
                # model with current policyid
                a = SrxAddress.objects.filter(
                    srcaddress__policyid=self.policyid)
                b = SrxAddrSet.objects.filter(
                    srcaddrset__policyid=self.policyid)
                if not a and not b:
                    self.fromzone.clear()
            elif src == 'to':
                a = SrxAddress.objects.filter(
                    destaddress__policyid=self.policyid)
                b = SrxAddrSet.objects.filter(
                    destaddrset__policyid=self.policyid)
                if not a and not b:
                    self.tozone.clear()

    def update_application(self, objectid, action):
        obj = SrxApplication.objects.filter(id=objectid).first()

        if action == 'add':
            self.application.add(obj)
        elif action == 'delete':
            self.application.remove(obj)

        return obj

    def update_appset(self, objectid, action):
        obj = SrxAppSet.objects.filter(id=objectid).first()

        if action == 'add':
            self.appset.add(obj)
        elif action == 'delete':
            self.appset.remove(obj)

        return obj
