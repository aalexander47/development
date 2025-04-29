import hashlib
import traceback
import sys
from django.dispatch import receiver
from django.db import transaction, IntegrityError, models
from django.core.signals import got_request_exception
from .models import ErrorLog  # Adjust this import as per your app structure

@receiver(got_request_exception)
def log_exception(sender, request, **kwargs):
    # Get the current exception info
    error_type, error_value, error_traceback = sys.exc_info()
    
    if not error_traceback:
        return  # Exit early if there's no traceback

    # Extract relevant traceback details
    last_traceback = traceback.extract_tb(error_traceback)[-1]
    file_name = last_traceback.filename
    line_number = last_traceback.lineno
    function_name = last_traceback.name
    full_traceback = ''.join(traceback.format_exception(error_type, error_value, error_traceback))
    request_url = request.build_absolute_uri() if request else None
    request_method = request.method if request else None
    request_data = None

    # Generate a unique identifier (uid) for the error
    uid = hashlib.md5(f"{file_name}{line_number}{function_name}{request_url}{request_method}".encode()).hexdigest()

    # Collect request details, if available
    if request and request.body:
        try:
            request_data = request.body.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            request_data = request.body.hex()  # Fallback to hex representation for non-decodable data

    # Attempt to log the error
    try:
        with transaction.atomic():
            # Try to create a new error log entry
            ErrorLog.objects.create(
                uid=uid,
                error_message=full_traceback,
                file_name=file_name,
                line_number=line_number,
                function_name=function_name,
                request_url=request_url,
                request_method=request_method,
                request_data=request_data,
                hit_count=1,  # Initial hit count
                status='new',  # Default status is "new"
            )
    except IntegrityError:
        # If the uid already exists, update the hit counter
        ErrorLog.objects.filter(uid=uid).update(
            hit_count=models.F('hit_count') + 1,
            status='new',  # Optional: Reset the status if the bug reoccurs
        )
