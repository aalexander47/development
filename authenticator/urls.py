from django.urls import path
from . import views

app_name = "auth"

urlpatterns = [
    path('auth-redirect/', views.auth_redirect_view, name='auth_redirect_view'),
    path('login/', views.login_request, name='login'),
    path('signup/', views.signup_request, name='signup'),
    path('temp-signup/', views.temp_signup, name="temp_signup"),
    path('logout/', views.logout_request, name='logout'),
    path('business-registration/', views.business_registration, name='business_registration'),
]