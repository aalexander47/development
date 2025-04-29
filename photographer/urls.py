from django.urls import path
from . import views

app_name = "photographer"

urlpatterns = [
    path('', views.home, name='home'),
    path('service/<str:service_id>/<str:slug>/', views.service_details, name='service'),
    path('service-rating/', views.service_rating, name='service_rating'),
    path('report-service/', views.report_service, name='report_service'),
    path('like/', views.toggle_like, name='Like'),
    path('save/', views.toggle_save, name='Save'),
    path('report-review/', views.report_review, name='report_review'),
    path('delete-review/', views.delete_review, name='delete_review'),
    # Search
    path('search/', views.search_by_service, name='search_service'),
    path('search/<str:category>/', views.search, name='search'),
    # CMS Routes
    path('dashboard/', views.cms_dashboard, name='Dashboard'),
    path('create/', views.cms_create, name='CreateService'),
    path('update/<str:id>/', views.cms_update, name='UpdateService'), 
    path('delete/', views.cms_delete_service, name='DeleteService'),
    path('load-categroy-form-component/', views.cms_load_category_form_component, name='LoadCategroyFormComponent'),
    path('gallery/', views.cms_gallery, name='Gallery'),
    path('gallery/delete/<str:id>/', views.cms_gallery_delete, name='GalleryDelete'),
    path('reviews/', views.cms_reviews, name='Reviews'),
    path('settings/', views.cms_settings, name='Settings'),
    # Leads
    path("request-callback/<str:service_id>/<str:slug>/<str:vendor_id>/", views.request_callback, name="request_callback"),
]