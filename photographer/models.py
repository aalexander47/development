from django.db import models
from vendor.models import Vendor, \
    Gallery as VendorGallery, \
    Like as VendorLike, \
    Save as VendorSave, \
    Review as VendorReview, \
    Lead as VendorLead
from user.models import \
    Like as UserLike, \
    Save as UserSave, \
    Review as UserReview, \
    Lead as UserLead
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from core.utils import compress_image

# Create your models here.
class Service(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer')
    category = models.CharField(max_length=150, null=True, blank=True) 
    other = models.JSONField(default=dict)
    description = models.TextField()
    contact = models.IntegerField(default=0, null=True, blank=True)
    experience = models.DateField(blank=True, null=True) 
    epss_reviews = models.JSONField(default=dict, blank=True, null=True)
    epss = models.JSONField(default=dict, blank=True, null=True) 
    price = models.IntegerField(default=0, blank=False, null=False)
    price_unit = models.CharField(max_length=20, null=True, blank=True, default='')
    policy = models.JSONField(default=dict, null=True, blank=True)
    ad_active = models.BooleanField(default=False, null=True, blank=True)
    recommendation_active = models.BooleanField(default=False, null=True, blank=True)
    sponsorship_active = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='service/photographer/thumbnail', null=True)
    i_agree = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is first created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the object is updated

    def verify(self):
        self.is_verified = True
        self.save()

    def unverify(self):
        self.is_verified = False
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

    def __str__(self):
        return f'{(self.category).capitalize()} Photographer'

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class Lead(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='leads')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_leads')
    lead_type = models.CharField(max_length=150, null=True, blank=True)
    uid = models.CharField(max_length=50, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lead_type
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        UserLead.objects.create(
            uid=self.uid
        )
        
        # Automatically create the corresponding VendorLead instance
        content_type = ContentType.objects.get_for_model(Lead)
        VendorLead.objects.get_or_create(
            vendor=self.vendor,
            content_type=content_type,
            object_id=self.id
        )


class CallbackRequest(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_callback_request')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='callback_request')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    uid = models.CharField(max_length=50, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f'{self.name} - {self.phone}'
    


class Gallery(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='gallery')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_gallery')
    image = models.ImageField(upload_to='service/photographer/gallery', null=True)
    album = models.CharField(max_length=150, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is first created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the object is updated
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Automatically create the corresponding VendorGallery instance
        content_type = ContentType.objects.get_for_model(Gallery)
        VendorGallery.objects.get_or_create(
            vendor=self.vendor,
            content_type=content_type,
            object_id=self.id
        )

    def __str__(self):
        return self.image.url

class LegalDetail(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='legal_details')
    payment_policy = models.TextField(blank=True, null=True)
    cancellation_policy = models.TextField(blank=True, null=True)
    terms_conditions = models.TextField(blank=True, null=True)
    refund_policy = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Review(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer_reviews')
    uid = models.CharField(max_length=10, default="", editable=False)
    review = models.TextField()
    rating = models.IntegerField(default=1, blank=False, null=False)
    approved = models.BooleanField(default=False, null=True, blank=True)
    recommend_for = models.JSONField(default=list, blank=True, null=True)  # for which eventron
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is first created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the object is updated

    def __str__(self):
        return self.review
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Automatically create the corresponding VendorReview instance
        content_type = ContentType.objects.get_for_model(Review)
        VendorReview.objects.get_or_create(
            vendor=self.vendor,
            content_type=content_type,
            object_id=self.id
        )
        # Automatically create the corresponding UserReview instance
        content_type = ContentType.objects.get_for_model(Review)
        UserReview.objects.get_or_create(
            user=self.user,
            content_type=content_type,
            object_id=self.id
        )
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    

class ReportService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer_reports')
    uid = models.CharField(max_length=10, default="", editable=False)
    reason = models.CharField(max_length=150)
    description = models.TextField()
    screenshot = models.ImageField(upload_to='reports/photographer/screenshot', null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.reason
    

class ReportReview(models.Model): 
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_report')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer_review_report')
    uid = models.CharField(max_length=10, default="", editable=False)
    reason = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.reason
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer_likes')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='likes')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_likes')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Automatically create the corresponding VendorLike instance
        content_type = ContentType.objects.get_for_model(Like)
        VendorLike.objects.get_or_create(
            vendor=self.vendor,
            content_type=content_type,
            object_id=self.id
        )
        # Automatically create the corresponding UserLike instance
        content_type = ContentType.objects.get_for_model(Like)
        UserLike.objects.get_or_create(
            user=self.user,
            content_type=content_type,
            object_id=self.id
        )
    

class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photographer_saves')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='saves')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='photographer_saves')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Automatically create the corresponding VendorSave instance
        content_type = ContentType.objects.get_for_model(Save)
        VendorSave.objects.get_or_create(
            vendor=self.vendor,
            content_type=content_type,
            object_id=self.id
        )
        # Automatically create the corresponding UserSave instance
        content_type = ContentType.objects.get_for_model(Save)
        UserSave.objects.get_or_create(
            user=self.user,
            content_type=content_type,
            object_id=self.id
        )