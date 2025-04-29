from django.db import models
from vendor.models import Vendor
from django.contrib.auth.models import User
import uuid

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=20)
    payment_for = models.CharField(max_length=20, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Get a custom description from kwargs or use a default one
        if self.status != 'CREATED':
            description = kwargs.pop('description', 'Payment via Razorpay')
            # Log the transaction on successful payment
            transaction = Transaction(
                user=self.user,
                amount=self.amount,
                transaction_type='credit',
                method='money',
                description=description, 
                razorpay_payment_id=self.payment_id,
            )
            if self.status == 'SUCCESS':
                transaction.is_successful = True
            else:
                transaction.is_successful = False
            transaction.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id
    

class Transaction(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    transaction_id = models.CharField(max_length=100, unique=True, blank=False, null=False)
    method = models.CharField(max_length=10, choices=[('money', 'Money'), ('point', 'Point')])
    description = models.TextField(null=True, blank=True)  # Transaction details or remarks
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)  # For external reference to Razorpay
    is_successful = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:  # Only generate if not present
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        # Use a UUID or customize it based on your needs (e.g., prefix, timestamp)
        return str(uuid.uuid4()).replace("-", "").upper()[:10]  # Generates a 10-character unique ID
    