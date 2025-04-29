from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Services, Gallery, Reviews, ReportService
from django.core.files.storage import default_storage


def test_create_service():
    thumbnail = SimpleUploadedFile("thumbnails/dd53a99b3cae8c8ea6654619c7765e57.png", b"file_content", content_type="image/jpeg")

    service = Services.objects.create(type='wedding', category='photography', thumbnail=thumbnail)
    
    Gallery.objects.create(service=service, image=thumbnail)
    Reviews.objects.create(service=service, review='Great service!')
    ReportService.objects.create(service=service, report='Some report')
    return service.id

def test_delete_service(pk):
    service = Services.objects.get(pk=pk)
    service.delete()

service_id = test_create_service()
test_delete_service(int(service_id) - 1)
# test_delete_service(11)

