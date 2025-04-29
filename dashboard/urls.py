from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_cms_view, name='Dashboard'),
    path("profile/", views.profile_cms_view, name="Profile"),
    path("settings/", views.settings_cms_view, name="Settings"),
    path("pricings/", views.pricings_cms_view, name="Pricings"),
    path("vendors/", views.vendors_cms_view, name="Vendors"),
    path("users/", views.users_cms_view, name="Users"),
    path("staffs/", views.staffs_cms_view, name="Staffs"),
    path('notifications/', views.notifications_cms_view, name='Notifications'),
    path('coupons/', views.coupons_cms_view, name='Coupons'),
    path('bugs/', views.bugs_cms_view, name='Bugs'),
    path('invitations/', views.invitations_cms_view, name='Invitations'),
    path('templates/', views.templates_cms_view, name='Templates'),
    path('invitations/chart-data/', views.invitations_chart_data, name='invitations_chart_data'),
    path('invitations/analytics-data/', views.invitations_analytics_data, name='invitations_analytics_data'),
    path('templates/analytics/', views.templates_analytics_view, name='TemplatesAnalytics'),  # New analytics page
    path('templates/<int:template_id>/reviews/', views.template_reviews_view, name='TemplateReviews'),
    path('templates/heatmap-data/', views.templates_heatmap_data, name='templates_heatmap_data'),
]