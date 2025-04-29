# tasks.py
# from celery import shared_task
from user.models import Notification  # Import your Notification model

# @shared_task
def create_notification(user_id, title, notification_type, description, other={}):
    # Create and save notification for the vendor
    notification = Notification.objects.create(
        user_id=user_id,
        title=title,
        type=notification_type,
        description=description,
        other=other
    )
    notification.save()
