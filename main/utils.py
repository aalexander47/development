import requests
import hashlib
from django.utils import timezone
from functools import wraps
from uuid import uuid4


def get_client_ip(request):
    """ Get the client's IP address from the request. """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Take the first IP if there are multiple
    else:
        ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
    return ip

def get_location_by_ip(ip):
    """ Get location details based on IP address using the ipinfo.io API. """
    try:
        # Replace with your ipinfo.io token if required
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        return {
            'ip': data.get('ip'),
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'postal': data.get('postal'),  # This is the postal code (PIN code)
            'loc': data.get('loc'),  # Latitude and Longitude
        }
    except Exception as e:
        return {'error': str(e)}

# Usage in a Django view
def get_user_location(request):
    ip = get_client_ip(request)
    location = get_location_by_ip(ip)
    return location

def set_anonymous_user_cookie(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Execute the view function to get the initial response
        response = view_func(request, *args, **kwargs)
        
        if request.user.is_authenticated and hasattr(response, 'set_cookie'):
            user_id = request.COOKIES.get('uid')
            
            if not user_id:
                # Generate a unique ID based on User Id and timestamp
                unique_string = f"user-{request.user.id}"
                user_id_hash = hashlib.md5(unique_string.encode()).hexdigest()

                # Set the cookie for 1 year
                response.set_cookie('uid', user_id_hash, max_age=365 * 24 * 60 * 60)
                
        # Check if the response is an HttpResponse to ensure we can set cookies
        elif request.user.is_anonymous and hasattr(response, 'set_cookie'):
            user_id = request.COOKIES.get('uid')
            
            if not user_id:
                # Generate a unique ID based on IP and timestamp
                get_ip = get_client_ip(request)
                user_ip = get_ip if get_ip else uuid4().hex
                unique_string = f"{user_ip}"
                user_id_hash = hashlib.md5(unique_string.encode()).hexdigest()

                # Set the cookie for 1 year
                response.set_cookie('uid', user_id_hash, max_age=365 * 24 * 60 * 60)
                
        return response
    return wrapper