import uuid
from django.db import models


class SrxZone(models.Model):
    zone_name = models.CharField(max_length=255)
    def __str__(self):
        return self.zone_name

class SrxAddress(models.Model):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    address_name = models.CharField(max_length=255)
    address_ip = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.address_name

class SrxAddrSet(models.Model):
    zone = models.ForeignKey(SrxZone, on_delete=models.CASCADE)
    addrset_name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    address = models.ManyToManyField(SrxAddress)
    def __str__(self):
        return self.addrset_name

class SrxProtocol(models.Model):
    protocol_type = models.CharField(max_length=3)
    def __str__(self):
        return self.protocol_type

class SrxApplication(models.Model):
    application_name = models.CharField(max_length=255)
    protocol = models.ForeignKey(SrxProtocol, on_delete=models.PROTECT, default=0)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    application_port = models.IntegerField()
    def __str__(self):
        return self.application_name

class SrxAppSet(models.Model):
    applicationset_name = models.CharField(max_length=255)
    applications = models.ManyToManyField(SrxApplication)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    def __str__(self):
        return self.applicationset_name

class SrxPolicy(models.Model):
    policy_name = models.CharField(max_length=255)
    from_zone = models.ManyToManyField(SrxZone, related_name='from_zones')
    to_zone = models.ManyToManyField(SrxZone, related_name='to_zones')
    source_address = models.ManyToManyField(SrxAddress, related_name='source_addresses')
    source_addrset = models.ManyToManyField(SrxAddrSet, related_name='source_addrsets')
    destination_address = models.ManyToManyField(SrxAddress, related_name='destination_addresses')
    destination_addrset = models.ManyToManyField(SrxAddrSet, related_name='destination_addrsets')
    applications = models.ManyToManyField(SrxApplication)
    appsets = models.ManyToManyField(SrxAppSet, related_name='appsets')
    def __str__(self):
        return self.policy_name
