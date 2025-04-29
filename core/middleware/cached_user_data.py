from django.core.cache import cache

class CachedUserDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f"user_data_{request.user.id}"
            user_data = cache.get(cache_key)

            if user_data is None:
                # Fetch user data
                groups = list(request.user.groups.values_list('name', flat=True))
                
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'groups': groups,  # Use cached groups
                    'profile_picture': (
                        request.user.userprofile.picture if hasattr(request.user, 'userprofile') and request.user.userprofile.picture else None
                    ),
                    'access_token': request.user.userprofile.access_token if hasattr(request.user, 'userprofile') else None,
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser,
                    'is_active': request.user.is_active,
                    'is_vendor': 'vendor' in groups,  # Use cached groups
                    'is_admin': 'admin' in groups,  # Use cached groups
                    'is_pending_payment': 'pending_payment' in groups  # Use cached groups
                }
                # Cache the user data for 6000 seconds
                cache.set(cache_key, user_data, timeout=6000)

            # Attach user_data to request.user
            request.user.cached_data = user_data

        response = self.get_response(request)
        return response
