from django.contrib import admin
from .models import ErrorLog, Contact

admin.site.site_header = "Eventic Admin"
admin.site.site_title = "Eventic"
admin.site.index_title = "Welcome to Eventic Admin"


admin.site.register(Contact)
admin.site.register(ErrorLog)
