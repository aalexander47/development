from django.core.management.base import BaseCommand
from vendor.models import Vendor, LegalDetails as VendorLegalDetails
from photographer.models import \
    Services as PhotographerServices, \
    Gallery as PhotographerGallery, \
    Reviews as PhotographerReviews, \
    ReportService as ReportPhotographerService

from django.db.models import Prefetch

class Command(BaseCommand):
    help = 'Transfer data from SourceModel to DestinationModel'

    def handle(self, *args, **kwargs):
        # Fetch all data from SourceModel
        source_data = ServiceImage.objects.all()

        # Create DestinationModel objects with the data from SourceModel
        destination_objects = []
        for item in source_data:
            vendor_instance = Vendor.objects.get(id=item.eventron_id)
            service_instance = PhotographerServices.objects.get(id=item.service_id)
            if service_instance and vendor_instance:
                destination_objects.append(PhotographerGallery(
                    id = item.id,
                    vendor = vendor_instance,
                    service = service_instance,
                    image = item.image,
                    description = item.description,
                    created_at = item.created_at,
                    updated_at = item.updated_at
                ))
        # Bulk create the new objects in DestinationModel
        PhotographerGallery.objects.bulk_create(destination_objects)

        self.stdout.write(self.style.SUCCESS('Successfully transferred data from SourceModel to DestinationModel'))
