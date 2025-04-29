from django.urls import path
from . import views

app_name = "vendor"

urlpatterns = [
    path('', views.dashboard_cms_view, name='Dashboard'),
    path('profile/', views.profile_cms_view, name='Profile'),
    path('details/', views.details_cms_view, name='Details'),
    path('services/', views.services_cms_view, name='Services'),
    path('notifications/', views.notifications_cms_view, name='Notifications'),
    path('billing/', views.billing_cms_view, name='Billing'),
    path('transactions/', views.transactions_cms_view, name='Transactions'),
    path('credit-plans/', views.credit_plans_cms_view, name='CreditPlans'),
    path('team/', views.team_cms_view, name='Team'),
    path('settings/', views.settings_cms_view, name='Settings'),
    path('epss/', views.eps_score_cms_view, name='EPSS'),
    path('legal/', views.legal_cms_view, name='Legal'),
    path('component/<str:component>/', views.get_component, name='get_component'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('approve-referral/<str:vendor_id>/', views.approve_referral, name='ApproveReferral'),
]

 