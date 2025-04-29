from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.eventic_homepage, name='home'),
    path('contact/', views.contact_request, name='contact'),
    path('about/', views.about_us_request, name='about'),
    path('terms-of-use/', views.terms_of_use_request, name='terms_of_use'),
    path('privacy-policy/', views.privacy_policy_request, name='privacy_policy'),
    path('payment-policy/', views.payment_policy_request, name='payment_policy'),
    path('refund-policy/', views.refund_policy_request, name='refund_policy'),
    # Eventron
    path('@<str:username>', views.vendor_request, name='vendor'),
    path('eventron/<str:account_id>/<str:slug>/', views.vendor_profile_request, name='Profile'),
    # Invitation
    path('invite/<int:id>/', views.invitation_detail, name='invitation'),
]