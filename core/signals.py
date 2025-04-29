# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache

@receiver(post_save, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    """
    Clears the cached user data when the User model is saved.
    """
    cache_key = f"auth_user_{instance.id}"
    cache.delete(cache_key)
