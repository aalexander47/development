from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blogs_view, name='Docs'),
    path('cms/dashboard/', views.blogs_cms_view, name='Dashboard'),
    path("cms/create/", views.blogs_create_cms_view, name="blogCreate"),
    path('cms/update/<str:id>', views.blogs_update_cms_view, name='blogUpdate'),
    path('cms/delete/<str:id>', views.blogs_delete_cms_view, name='blogDelete'),
    path("cms/blog/", views.blogs_cms_view, name="blogs"),
    path("cms/media/", views.media_cms_view, name="Media"),
    path("cms/media-delete/", views.media_delete_cms_view, name="MediaDelete"),
    path('search/', views.search_view, name='Search'),
    path('cms/sitemap/', views.sitemap_view, name='Sitemap'),
    path('save_blog/<str:blog_id>', views.save_blog, name='save_blog'),
    path("<str:blog_url>/", views.blog_view, name='Blog'),
]