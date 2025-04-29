from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from user.models import Notification
from main.models import ErrorLog
from django_ratelimit.decorators import ratelimit

# @ratelimit(key='user', rate='5/m', method='GET', block=True)  # Limit to 5 requests per minute
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_count(request):
    user = request.user
    cache_key = f'notification_count_{user.id}'
    count = cache.get(cache_key)

    if not count:  # Cache miss
        notification_count = Notification.objects.filter(user=user, seen=False).count()
        cache.set(cache_key, count, timeout=60*60)  # Cache for 1 hour

    _data = {
        'notification_count': notification_count,
        'bug_count': 0
    }

    # Check if the user is an admin or developer or superuser
    if user.is_superuser or request.user.groups.filter(name__in=['admin', 'developer']).exists():
        cache_key = 'bug_count'
        bug_count = cache.get(cache_key)

        if not bug_count:  # Cache miss
            bug_count = ErrorLog.objects.filter(seen=False).count()
            cache.set(cache_key, bug_count, timeout=60*60)  # Cache for 1 hour

        _data['bug_count'] = bug_count

    return Response(_data)


def vendor_analytics(request):
    # Get the number of vendors
    # Get 
    _data = {
        'vendor_count': 0
    }
    return JsonResponse(_data)