from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Vendor, ReportIssue
from payment.models import Transaction

@receiver(pre_delete, sender=Vendor)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        if default_storage.exists(instance.profile_picture.name):
            instance.profile_picture.delete(save=False)
            

@receiver(pre_delete, sender=ReportIssue)
def delete_report_issue_ss(sender, instance, **kwargs):
    if instance.screenshot:
        if default_storage.exists(instance.screenshot.name):
            instance.screenshot.delete(save=False)
            