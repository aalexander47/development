from django.urls import path
from . import views

app_name = 'docs'

urlpatterns = [
    path('', views.docs_view, name='Docs'),
    path('cms/dashboard/', views.docs_cms_view, name='Dashboard'),
    path("cms/create/", views.docs_create_cms_view, name="DocsCreate"),
    path('cms/update/<str:id>', views.docs_update_cms_view, name='DocsUpdate'),
    path('cms/delete/<str:id>', views.docs_delete_cms_view, name='DocsDelete'),
    path("cms/articles/", views.articles_cms_view, name="Articles"),
    path("cms/media/", views.media_cms_view, name="Media"),
    path("cms/media-delete/", views.media_delete_cms_view, name="MediaDelete"),
    path('search/', views.search_view, name='Search'),
    path('article/<str:id>', views.article_view, name='Article'),
    path('cms/sitemap/', views.sitemap_view, name='Sitemap'),
    path('save_article/<str:article_id>', views.save_article, name='save_article'),
    path("<str:doc_url>/", views.doc_view, name='Doc'),
]