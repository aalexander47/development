from django.core.cache import cache
from django.shortcuts import redirect

def has_permission(allowed_groups, url="auth:auth_redirect_view"):
    def _method_wrapper(view_method):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                # Get the current page URL
                current_url = request.path
                next = f"?next={current_url}" if current_url else ""
                return redirect(f'/auth/login{next}')

            # Cache key based on user ID and allowed groups
            # cache_key = f"user_groups_{user.id}"
            # user_groups = cache.get(cache_key)

            # if user_groups is None:
            #     # If not in cache, query the database and set the cache
            #     user_groups = list(user.groups.values_list('name', flat=True))
            #     cache.set(cache_key, user_groups, timeout=600)  # Cache for 10 minutes

            user_groups = list(user.groups.values_list('name', flat=True))
            permissions = allowed_groups.replace(" ", ",").split(",")

            for group in permissions:
                if group in user_groups:
                    return view_method(request, *args, **kwargs)
                
            if user.is_superuser:
                return redirect("admin:index")

            if user.is_staff:
                return redirect("dashboard:Dashboard")
            elif "vendor" in user_groups:
                return redirect("vendor:Dashboard")
            else:
                return redirect(url)
        return _wrapped_view
    return _method_wrapper

def is_not_member(not_allowed_groups, url="auth:auth_redirect_view"):
    def _method_wrapper(view_method):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Get the current page URL
                current_url = request.path
                next = f"?next={current_url}" if current_url else ""
                return redirect(f'/auth/signup{next}')

            # Cache key based on user ID and not allowed groups
            # cache_key = f"user_groups_{request.user.id}"
            # user_groups = cache.get(cache_key)

            # if user_groups is None:
            #     # If not in cache, query the database and set the cache
            #     user_groups = list(request.user.groups.values_list('name', flat=True))
            #     cache.set(cache_key, user_groups, timeout=600)  # Cache for 10 minutes

            user_groups = list(request.user.groups.values_list('name', flat=True))
            permissions = not_allowed_groups.replace(" ", ",").split(",")

            for group in permissions:
                if group in user_groups:
                    return redirect(url)

            return view_method(request, *args, **kwargs)
        return _wrapped_view
    return _method_wrapper
