import uuid
from django.db import models


class SrxZone(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class SrxAddress(models.Model):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.name

class SrxAddrSet(models.Model):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    addresses = models.ManyToManyField(SrxAddress, related_name='addresses')
    def __str__(self):
        return self.name

class SrxProtocol(models.Model):
    ptype = models.CharField(max_length=3)
    def __str__(self):
        return self.ptype

class SrxApplication(models.Model):
    name = models.CharField(max_length=255)
    protocol = models.ForeignKey(SrxProtocol, on_delete=models.PROTECT,
                                 default=0)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    port = models.CharField(max_length=11)
    def __str__(self):
        return self.name

class SrxAppSet(models.Model):
    name = models.CharField(max_length=255)
    applications = models.ManyToManyField(SrxApplication,
                                          related_name='applications')
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.name

class SrxPolicy(models.Model):
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
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.name
