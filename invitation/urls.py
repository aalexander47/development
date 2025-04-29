from django.urls import path
from . import views

app_name = 'invitation'

urlpatterns = [
    path('', views.home, name='home'),
    path("template/<int:id>/", views.template_information, name='template_information'),
    path("preview/<str:id>/", views.template_preview, name='template_preview'),
    path('wedding/rsvp/', views.wedding_rsvp, name='wedding_rsvp'),
    path('create/<str:id>/', views.create_invitation, name='create_invitation'),
    path('update/<int:id>/', views.update_invitation, name='update_invitation'),
    path('delete/<int:id>/', views.delete_invitation, name='delete_invitation'),
    path('<str:invitation_type>/<str:template_id>/payment/', views.invitation_payment, name='invitation_payment'),
    path('generate-payment/', views.generate_payment, name='generate_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    # Cms routes
    path('dashboard/<str:id>/', views.cms_invitation_dashboard, name='cms_dashboard'),
    path('rsvps/<str:id>/', views.cms_invitation_rsvps, name='cms_rsvps'),

]

urlpatterns += [
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/report/', views.report_review, name='report_review'),  # New URL for reporting reviews
    path('review/pin-unpin/<str:review_id>/<str:template_id>/', views.toggle_pin_unpin_review, name='toggle_pin_unpin_review'),  # New URL for pinning/unpinning reviews
    path('template/<int:template_id>/report/', views.report_template, name='report_template'),  # New URL for reporting templates
    path('template/<int:template_id>/add-review/', views.add_review, name='add_review'),
    path('template/add-new/', views.add_template, name='add_template'),  # Add template
    path('template/<int:template_id>/edit/', views.edit_template, name='edit_template'),  # Edit template
    path('template/<int:template_id>/like/', views.toggle_like_template, name='toggle_like_template'),
    path('template/<int:template_id>/save/', views.toggle_save_template, name='toggle_save_template'),
]