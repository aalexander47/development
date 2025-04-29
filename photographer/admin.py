from django.contrib import admin
from .models import Service, ReportService, ReportReview, CallbackRequest, Lead

# Register your models here.
admin.site.register(Service)
admin.site.register(ReportService)
admin.site.register(ReportReview)
admin.site.register(CallbackRequest)
admin.site.register(Lead)