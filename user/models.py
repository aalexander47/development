from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from dirtyfields import DirtyFieldsMixin

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='user/profile_pictures/', blank=True, null=True)
    phone = models.CharField(max_length=20, default="", blank=True, null=True, unique=True)

    def __str__(self):
        return self.phone
    

class Notification(DirtyFieldsMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notification')
    title = models.CharField(max_length=100, default="", editable=False)
    type = models.CharField(max_length=100, default="", editable=False)
    description = models.TextField(blank=True, null=True)
    other = models.JSONField(default=dict, blank=True, null=False)
    is_read = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Invalidate cache on creation or update
        cached_notification_count_key = f'notification_count_{self.user.id}'
        cached_notification_key = f'cached_notifications_{self.user.id}'
        cached_unread_key = f'cached_unread_notifications_{self.user.id}'

        # Check if the object is being created (no primary key) or if 'seen' field is updated
        if not self.pk or 'seen' in self.get_dirty_fields():  # On new creation or when 'seen' changes
            cache.delete(cached_notification_count_key)
            cache.delete(cached_notification_key)
            cache.delete(cached_unread_key)

        super().save(*args, **kwargs)
        

class Lead(models.Model):
    uid = models.CharField(max_length=50, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='user_likes')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saves')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='user_saves')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='user_reviews')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')