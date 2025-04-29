from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path('', views.vendor_search, name='Vendor_Search'),
]