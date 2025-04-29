from django.urls import path
from . import views

app_name = 'credit'

urlpatterns = [
    path('', views.index, name='home'),
]