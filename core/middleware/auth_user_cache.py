# core/middleware/auth_user_cache.py

from django.core.cache import cache
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User

def get_cached_user(user_id):
    cache_key = f"auth_user_{user_id}"
    user = cache.get(cache_key)

    if user is None:
        try:
            user = User.objects.get(pk=user_id)
            cache.set(cache_key, user, timeout=300)  # Cache for 5 minutes
        except User.DoesNotExist:
            return None

    return user

def CachedUserMiddleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            request.user = SimpleLazyObject(lambda: get_cached_user(request.user.id))
        else:
            request.user = SimpleLazyObject(lambda: None)

        response = get_response(request)
        return response

    return middleware
