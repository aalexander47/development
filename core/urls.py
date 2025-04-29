from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import PasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include("debug_toolbar.urls")),
    path('', include('main.urls', namespace='main')),
    path('api/', include('api.urls', namespace='api')),
    path('auth/', include('authenticator.urls', namespace='auth')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('user/', include('user.urls', namespace='user')),
    path('search/', include('search.urls', namespace='search')),
    path('docs/', include('docs.urls', namespace='docs')),
    path('blog/', include('blog.urls', namespace='blog')),
    # path('credit/', include('credit.urls', namespace='credit')),
    # Social Login
    path("accounts/login/", lambda request: redirect("/auth/login/", permanent=True)),  # Redirect old login URL
    # path('accounts/password/reset/', PasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/', include('allauth.urls')),
    # Analytics
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    # vendor urls
    path('vendor/', include('vendor.urls', namespace='vendor')),
    # services urls
    path('photographer/', include('photographer.urls', namespace='photographer')),
    path('videographer/', include('videographer.urls', namespace='videographer')),
    # Invitations
    path('invitation/', include('invitation.urls', namespace='invitation')),
]


handler400 = 'main.errors.custom_400'
handler403 = 'main.errors.custom_403'
handler404 = 'main.errors.custom_404'
handler500 = 'main.errors.custom_500'


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 