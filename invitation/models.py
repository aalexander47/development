from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string
import uuid  # Add this import for generating unique IDs


def generate_unique_invitation_uid():
    while True:
        uid =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return uid
        
def generate_unique_template_uid():
    while True:
        uid =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return uid

def generate_unique_review_uid():
    return str(uuid.uuid4())[:8]  # Generate a unique 8-character UID

class Template(models.Model):
    TYPES = [
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday'),
        ('engagement', 'Engagement'),
        ('anniversary', 'Anniversary'),
        ('baby_shower', 'Baby Shower'),
        ('party', 'Party')
    ]
    uid = models.CharField(max_length=8, unique=True, default=generate_unique_template_uid, null=False, blank=False, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitation_templates')
    invitation_type = models.CharField(max_length=100, choices=TYPES)
    template_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()  # Supports rich text content
    thumbnail = models.URLField(max_length=200, blank=True, null=True)  # URL field for thumbnail
    info = models.JSONField(default=dict, blank=True, null=True)
    price = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    free_days = models.IntegerField(default=0)
    unit = models.CharField(max_length=100, default='day')
    path = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Invitation(models.Model):
    uid = models.CharField(max_length=8, unique=True, default=generate_unique_invitation_uid, null=False, blank=False, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Invitation Template", related_name='invitations')
    details = models.JSONField(default=dict, blank=True, null=False, verbose_name="details")
    start_date = models.DateField(verbose_name="Invitation Start Date")
    end_date = models.DateField(verbose_name="Invitation End Date")
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def is_expired(self):
        return timezone.now().date() > self.end_date
    

class RSVP(models.Model):
    TEAM = [
        ('groom', 'Groom'),
        ('bride', 'Bride'),
        ('both', 'Both'),
        ('none', 'None'),
        ('other', 'Other')
    ]
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='rsvps')
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    ATTENDING_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('maybe', 'Maybe'),
    ]
    attending = models.CharField(max_length=10, choices=ATTENDING_CHOICES, default='yes')
    message = models.TextField(null=True, blank=True)
    team = models.CharField(max_length=100, choices=TEAM, default='groom')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    uid = models.CharField(max_length=10, unique=True, default=generate_unique_review_uid, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitation_reviews')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    other = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flagged = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)  # Field to mark a review as pinned
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    def save(self, *args, **kwargs):
        if self.pinned:
            # Unpin other reviews for the same template
            Review.objects.filter(template=self.template, pinned=True).update(pinned=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review by {self.user} on {self.template}"

class TemplateReport(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_reports')
    uid = models.CharField(max_length=10, unique=True, default="", editable=False)
    reason = models.CharField(max_length=150)   
    description = models.TextField()
    screenshot = models.ImageField(upload_to='reports/invitation/template/screenshot', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reason

class ReportReview(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_review_reports')
    uid = models.CharField(max_length=10, unique=True, default="", editable=False)
    reason = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reason

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_likes')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='template_likes')
    created_at = models.DateTimeField(auto_now_add=True)

class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_saves')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='template_saves')
    created_at = models.DateTimeField(auto_now_add=True)
