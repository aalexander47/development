from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from dashboard.models import Coupon
from django.core.cache import cache
from dirtyfields import DirtyFieldsMixin
from django.utils.timezone import now
import random
import string
from django.conf import settings
from user.models import Notification



def generate_unique_account_id():
    while True:
        account_id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Vendor.objects.filter(account_id=account_id).exists():
            return account_id
        

# Create your models here.
class Vendor(models.Model):
    account_id = models.CharField(max_length=8, unique=True, default=generate_unique_account_id, null=False, blank=False, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='vendor/profile_pictures', null=True, blank=True)
    other = models.JSONField(default=dict, blank=True, null=False)
    # Contact Details
    email = models.EmailField(null=True, default="", blank=True)
    phone = models.CharField(max_length=20, null=True, default="")
    whatsapp = models.CharField(max_length=20, null=True, default="")
    # Contact Time 
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    # Address Details
    address = models.CharField(max_length=150, default="", blank=True, null=False)
    city = models.CharField(max_length=100, default="", blank=True, null=False)
    state = models.CharField(max_length=100, default="", blank=True, null=False)
    country = models.CharField(max_length=100, default="India", null=False)
    pincode = models.IntegerField(default=0, blank=True, null=False)
    embed_map = models.TextField(blank=True, default="", null=False)
    # Social Feeds
    website = models.URLField(blank=True, null=True, default="")
    facebook = models.URLField(blank=True, null=True, default="")
    instagram = models.URLField(blank=True, null=True, default="")
    twitter = models.URLField(blank=True, null=True, default="")
    # My Feature
    active_services = models.JSONField(default=dict, blank=True, null=False)
    active_features = models.JSONField(default=dict, blank=True, null=False)
    epss = models.JSONField(default=dict, blank=True, null=False)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    is_suspended = models.BooleanField(default=False, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    sponsorship_active = models.BooleanField(default=False, null=True, blank=True)
    in_service_recommendation = models.BooleanField(default=True, null=True, blank=True)
    # Credit
    credits = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    bill = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Used credits
    auto_bill_settlement_credits = models.BooleanField(default=True)
    bill_payment_alert_count = models.IntegerField(default=0)
    # Autofields
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    def add_credit(self, amount):
        """Add credits to the vendor's account."""
        self.credits += amount

    def deduct_credit(self, amount):
        """Deduct credits from the vendor's available balance."""
        if self.credits >= amount:
            self.credits -= amount
            if self.is_suspended:
                self.unsuspend()
        else:
            self.credits -= amount
            self.suspend()
            raise ValueError("Insufficient credits")

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

    def suspend(self):
        self.is_suspended = True
        self.save()

    def unsuspend(self):
        self.is_suspended = False
        self.save()

    def delete(self, *args, **kwargs):
        # Remove vendor group from user
        user = self.user
        user.groups.remove(Group.objects.get(name='vendor'))
        user.groups.remove(Group.objects.get(name='pending_payment'))
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name 
    

class TrackBilling(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='track_billing')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active_services = models.JSONField(default=dict, blank=True, null=False)
    active_features = models.JSONField(default=dict, blank=True, null=False)
    other = models.JSONField(default=dict, blank=True, null=False)
    pricing = models.JSONField(default=dict, blank=True, null=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    

class Service(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='services')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_services')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')    


class Lead(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='leads')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_leads')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Gallery(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='gallery')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_gallery')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class LegalDetail(models.Model):
    vendor = models.OneToOneField(Vendor, unique=True, on_delete=models.CASCADE, related_name='legal')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='legal')
    payment_policy = models.TextField(blank=True, null=True)
    cancellation_policy = models.TextField(blank=True, null=True) 
    terms_conditions = models.TextField(blank=True, null=True)
    refund_policy = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_likes')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Save(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='saves')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_saves')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Review(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vendor_reviews')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class ReportIssue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_issue')
    title = models.CharField(max_length=100, default="", editable=False)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)
    screenshot = models.ImageField(upload_to='report_issue/screenshots', null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.title
    

class TeamMember(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='team')
    name = models.CharField(max_length=100, default="")
    role = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=100, default="")
    whatsapp = models.CharField(max_length=100, default="")
    email = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AppliedCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="applied_coupons")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="applied_coupons")
    code = models.CharField(max_length=10, default="", editable=False)
    info = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor} - {self.coupon.code}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Send notification to vendor
        Notification.objects.create(
            user=self.vendor.user,
            title="Coupon Applied",
            type="coupon_applied",
            description=f"You have applied the coupon &nbsp;<strong>{self.coupon.code}</strong>.",
            other={
                "coupon_id": self.coupon.id,
                "vendor_id": self.vendor.id,
                "vendor_name": self.vendor.name,
                "coupon_code": self.coupon.code,
            }
        )

class AppliedReferral(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="applied_referrals")
    referred_by = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="referred_vendors")
    code = models.CharField(max_length=20, default="", editable=False)
    info = models.JSONField(default=dict, blank=True, null=False)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor} - {self.code}"
    
    # On Create send notification to vendor_uid
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.approved:
            # Send notification asking to approve the referral
            Notification.objects.create(
                user=self.referred_by.user,
                title="Request for Referral Approval",
                type="referral_approval",
                description=f"Vendor {self.vendor.name} has applied for referral.",
                other={
                    "vendor_id": self.vendor.id,
                    "vendor_name": self.vendor.name,
                    "vendor_account_id": self.vendor.account_id,
                    "vendor_email": self.vendor.email,
                    "vendor_phone": self.vendor.phone,
                    "message": f"Vendor <strong>{self.vendor.name}</strong> has applied for referral. If you know this vendor, You can approve the referral. You will be credited with 50 credit points.",
                }
            )
        else:
            # Send notification to vendor that referral has been approved
            Notification.objects.create(
                user=self.vendor.user,
                title="Referral Approved",
                type="referral_approved",
                description=f"Vendor {self.referred_by.name} has approved the referral.",
                other={
                    'message':f"Vendor <strong>{self.referred_by.name}</strong> has approved the referral. We have credited you with 100 credit points.",
                }
            )