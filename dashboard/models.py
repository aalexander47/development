from django.db import models
from django.utils.timezone import now


class Pricing(models.Model):
    name = models.CharField(max_length=100, default="", null=True, blank=True)
    tag = models.CharField(max_length=100, null=True, blank=True, unique=True) # e.g. photographer_wedding
    category = models.CharField(max_length=100, default="", null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True) # Allow up to 2 decimal places
    unit = models.CharField(max_length=100, null=True, blank=True, choices=[('D', 'Daily'), ('O', 'Once'), ('M', 'Monthly')]) # Daily, Once, Monthly
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is first created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the object is updated

    def __str__(self):
        return f"{self.tag} - {self.category} - Rs.{self.price} / {self.unit}"
    

class Coupon(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)  # Unique coupon code
    description = models.TextField(null=True, blank=True)  # Description of the coupon
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)  # Fixed discount
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)  # % discount
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)  # Max discount (for %)
    is_active = models.BooleanField(default=True)  # Whether the coupon is active
    start_date = models.DateTimeField(default=now)  # Coupon validity start date
    end_date = models.DateTimeField()  # Coupon validity end date
    credits = models.PositiveIntegerField(default=0, null=True, blank=True)  # Number of credits required
    usage_limit = models.PositiveIntegerField(default=None, null=True, blank=True)  # Maximum number of uses
    usage_count = models.PositiveIntegerField(default=0, null=True, blank=True)  # Number of times the coupon has been used
    applicable_at = models.JSONField(default=dict)  # Applicable for Redumptions, Credit Purchase, Registration. 
    skip_payment = models.BooleanField(default=False)  # Skip payment if the coupon is applied
    combined_referral = models.BooleanField(default=False)  # Can be combined with referral
    created_at = models.DateTimeField(auto_now_add=True)  # When the coupon was created

    def is_valid(self):
        """Checks if the coupon is valid."""
        return (
            self.is_active and
            (self.start_date <= now() <= self.end_date) and
            (self.usage_limit is None or self.usage_count < self.usage_limit)
        )

    def __str__(self):
        return self.code
    