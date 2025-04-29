from django.urls import path
from . import views
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

app_name = "api"

urlpatterns = [
    # Other URL patterns
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('notifications/count/', views.notification_count, name='NotificationCount'),
    # Vendor URL patterns
    path('vendors/analytics', views.vendor_analytics, name='VendorAnalytics'),
    # path('vendor/<int:vendor_id>/analytics', views.vendor_analytics, name='VendorAnalytics'),
    # Photographer URL patterns
    # path('photographer/<int:photographer_id>/analytics', views.photographer_analytics, name='PhotographerAnalytics'),
]