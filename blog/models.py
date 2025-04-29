from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    url = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    recommendation_title = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    recommendation_thumbnail = models.CharField(max_length=255, blank=True, null=True)
    previous_blog = models.ForeignKey('self', related_name='previous', blank=True, null=True, on_delete=models.SET_NULL)
    next_blog = models.ForeignKey('self', related_name='next', blank=True, null=True, on_delete=models.SET_NULL)
    recommendation_blog = models.ForeignKey('self', related_name='recommendation', blank=True, null=True, on_delete=models.SET_NULL)
    content_data = models.JSONField(blank=True, null=True)  # JSON field for content
    seo_data = models.JSONField(blank=True, null=True)  # JSON field for SEO
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class BlogMedia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs_media')
    image = models.ImageField(upload_to='blog/media', null=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is first created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the object is updated
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.image.url
