from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('', views.profile_cms_view, name='Profile'),
    path('likes/', views.likes_cms_view, name='Likes'),
    path('saves/', views.saves_cms_view, name='Saves'),
    path('notifications/', views.notifications_cms_view, name='Notifications'),
    path('invitations/', views.invitations_cms_view, name='Invitations'),
    path('likes/service/', views.likes_service_view, name='LikesService'),
    path('likes/template/', views.likes_template_view, name='LikesTemplate'),
    path('saves/service/', views.saves_service_view, name='SavesService'),
    path('saves/template/', views.saves_template_view, name='SavesTemplate'),
]