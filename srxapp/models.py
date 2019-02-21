from django.db import models


class BaseModel(models.Model):

    class Meta:
        abstract = True
        app_label = 'srxapp'


class SrxZone(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SrxAddress(BaseModel):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SrxAddrSet(BaseModel):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    addresses = models.ManyToManyField(SrxAddress, related_name='addresses')

    def __str__(self):
        return self.name


class SrxProtocol(BaseModel):
    ptype = models.CharField(max_length=12)

    def __str__(self):
        return self.ptype


class SrxApplication(BaseModel):
    name = models.CharField(max_length=255)
    protocol = models.ForeignKey(SrxProtocol, on_delete=models.CASCADE, default=0)
    port = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class SrxAppSet(BaseModel):
    name = models.CharField(max_length=255)
    applications = models.ManyToManyField(SrxApplication, related_name='applications')

    def __str__(self):
        return self.name


class SrxPolicy(BaseModel):

    name = models.CharField(max_length=255)
    fromzone = models.ManyToManyField(SrxZone, related_name='fromzone')
    tozone = models.ManyToManyField(SrxZone, related_name='tozone')
    srcaddress = models.ManyToManyField(SrxAddress, related_name='srcaddress')
    srcaddrset = models.ManyToManyField(SrxAddrSet, related_name='srcaddrset')
    destaddress = models.ManyToManyField(SrxAddress, related_name='destaddress')
    destaddrset = models.ManyToManyField(SrxAddrSet, related_name='destaddrset')
    application = models.ManyToManyField(SrxApplication, related_name='application')
    appset = models.ManyToManyField(SrxAppSet, related_name='appset')

    def __str__(self):
        return self.name
