from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import UserProfile

@receiver(pre_delete, sender=UserProfile)
def delete_user_profile_picture(sender, instance, **kwargs):
    if instance.picture:
        if default_storage.exists(instance.picture.name):
            instance.picture.delete(save=False)
