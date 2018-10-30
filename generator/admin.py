from django.contrib import admin

# Register your models here.

from .models import SrxZone, SrxAddress, SrxAddrSet, SrxApplication, SrxAppSet, SrxPolicy, SrxProtocol

admin.site.register(SrxPolicy)
admin.site.register(SrxZone)
admin.site.register(SrxAddress)
admin.site.register(SrxAddrSet)
admin.site.register(SrxApplication)
admin.site.register(SrxAppSet)
admin.site.register(SrxProtocol)