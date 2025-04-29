from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Service, Gallery, ReportService, Like, Save, Review
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from vendor.models import \
    Gallery as VendorGallery, \
    Like as VendorLike, \
    Save as VendorSave, \
    Review as VendorReview, \
    Service as VendorService
from user.models import \
    Like as UserLike, \
    Save as UserSave, \
    Review as UserReview


@receiver(post_save, sender=Service)
def save_service(sender, instance, **kwargs):
    vendor = instance.vendor
    service_tag = f'videographer_{(instance.category).lower()}-[{instance.id}]'
    vendor.active_services[service_tag] = instance.is_active
    vendor.save()


@receiver(pre_delete, sender=Service)
def delete_service(sender, instance, **kwargs):
    if instance.thumbnail:
        if default_storage.exists(instance.thumbnail.name):
            instance.thumbnail.delete(save=False)

    service_tag = f'videographer_{(instance.category).lower()}-[{instance.id}]'

    vendor = instance.vendor
    # Remove the service name from the active_services list
    if service_tag in vendor.active_services:
        del vendor.active_services[service_tag]
        vendor.save()

    # Find and delete the related VendorService instance
    content_type = ContentType.objects.get_for_model(Service)
    VendorService.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()


@receiver(pre_delete, sender=Gallery)
def delete_gallery_image(sender, instance, **kwargs):
    if instance.image:
        if default_storage.exists(instance.image.name):
            instance.image.delete(save=False)


# Signal handler to delete the related VendorGallery object
@receiver(post_delete, sender=Gallery)
def delete_related_vendorgallery(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(Gallery)
    
    # Find and delete the related VendorGallery instance
    VendorGallery.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()


@receiver(post_delete, sender=Like)
def delete_related_like(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(Like)
    
    # Find and delete the related VendorGallery instance
    VendorLike.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()
    UserLike.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()


@receiver(post_delete, sender=Save)
def delete_related_save(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(Save)
    
    # Find and delete the related VendorGallery instance
    VendorSave.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()
    UserSave.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()


@receiver(post_delete, sender=Review)
def delete_related_review(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(Review)
    
    # Find and delete the related VendorGallery instance
    VendorReview.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()
    UserReview.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()
    

@receiver(pre_delete, sender=ReportService)
def delete_report_screenshot(sender, instance, **kwargs):
    if instance.screenshot:
        if default_storage.exists(instance.screenshot.name):
            instance.screenshot.delete(save=False)