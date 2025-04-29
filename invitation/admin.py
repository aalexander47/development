from django.contrib import admin
from .models import Template, Invitation, RSVP, Like, Save, Review

# Register your models here.
admin.site.register(Template)
admin.site.register(Invitation)
admin.site.register(RSVP)
admin.site.register(Like)
admin.site.register(Save)
admin.site.register(Review)