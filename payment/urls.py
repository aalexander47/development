from django.urls import path
from .views import handle_payment_success, business_registration_payment, calculate_price, apply_code

app_name = "payment"

urlpatterns = [
    path('business-registration-payment/', business_registration_payment, name='business_registration_payment'),
    path('handle-payment-success/', handle_payment_success, name='handle_payment_success'),
    path('calculate-price/', calculate_price, name='CalculatePrice'),
    path('apply-code/', apply_code, name='ApplyCode'),
]