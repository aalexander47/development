from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    uid = models.CharField(max_length=50, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class ErrorLog(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    uid = models.CharField(max_length=50, unique=True, null=True, blank=True)
    error_message = models.TextField()  # Full error message or details
    file_name = models.CharField(max_length=255, null=True, blank=True)  # File where the error occurred
    line_number = models.IntegerField(null=True, blank=True)  # Line number of the error
    function_name = models.CharField(max_length=255, null=True, blank=True)  # Function name where the error occurred
    request_url = models.URLField(null=True, blank=True)  # URL where the error occurred
    request_method = models.CharField(max_length=10, null=True, blank=True)  # GET, POST, etc.
    request_data = models.TextField(null=True, blank=True)  # Data submitted with the request
    hit_count = models.PositiveIntegerField(default=1)  # Added field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')  # Status of the bug
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the error
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Error in File:{self.file_name} - Line: {self.line_number}"