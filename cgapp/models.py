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
    address = models.ManyToManyField(SrxAddress)
    def __str__(self):
        return self.name

class SrxProtocol(models.Model):
    ptype = models.CharField(max_length=3)
    def __str__(self):
        return self.ptype

class SrxApplication(models.Model):
    name = models.CharField(max_length=255)
    protocol = models.ForeignKey(SrxProtocol, on_delete=models.PROTECT, default=0)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    port = models.IntegerField()
    def __str__(self):
        return self.name

class SrxAppSet(models.Model):
    name = models.CharField(max_length=255)
    applications = models.ManyToManyField(SrxApplication)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.name

class SrxPolicy(models.Model):
    name = models.CharField(max_length=255)
    fromzone = models.ManyToManyField(SrxZone, related_name='fromzones')
    tozone = models.ManyToManyField(SrxZone, related_name='tozones')
    srcaddress = models.ManyToManyField(SrxAddress, related_name='srcaddresses')
    srcaddrset = models.ManyToManyField(SrxAddrSet, related_name='srcaddrsets')
    destaddress = models.ManyToManyField(SrxAddress, related_name='destaddresses')
    destaddrset = models.ManyToManyField(SrxAddrSet, related_name='destaddrsets')
    applications = models.ManyToManyField(SrxApplication)
    appsets = models.ManyToManyField(SrxAppSet, related_name='appsets')
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.name

class SrxNewConfig(models.Model):
    configid = models.CharField(max_length=255, default='', primary_key=True)
    fromzone = models.CharField(max_length=255, default='')
    tozone = models.CharField(max_length=255, default='')
    source = models.CharField(max_length=255, default='')
    destination = models.CharField(max_length=255, default='')
    applications = models.CharField(max_length=255, default='')
    def __str__(self):
        return self.configid