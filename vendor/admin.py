from django.contrib import admin
from .models import Vendor, ReportIssue, Service

# Register your models here.
admin.site.register(Vendor)
admin.site.register(ReportIssue)
admin.site.register(Service)