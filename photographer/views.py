from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
import hashlib, random, re

from vendor.models import \
    Vendor, \
    Service as VendorService, \
    Lead as VendorLead, \
    Gallery as VendorGallery, \
    TeamMember

from user.models import \
    Lead as UserLead

from .models import \
    Service as PhotographerService, \
    Review as PhotographerReview, \
    ReportService as ReportPhotographerService, \
    ReportReview as ReportPhotographerReview, \
    Gallery as PhotographerGallery, \
    Lead as PhotographerLead, \
    Like as PhotographerLike, \
    Save as PhotographerSave, \
    CallbackRequest as PhotographerCallbackRequest

from django.db.models import Q, Count, F, Value, CharField, Prefetch, Exists, OuterRef, IntegerField, When, Case
from django.db.models.functions import Concat
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from authenticator.decorators import has_permission
from core.utils import compress_image
from uuid import uuid4
from django.conf import settings
from django.contrib import messages
from datetime import date, datetime, timedelta
from .tasks import send_callback_lead_email
from dashboard.data import services as photographer_services
from vendor.tasks import create_notification
from user.utils import get_cached_user
from main.utils import get_client_ip, set_anonymous_user_cookie

#/////////////////   CMS   ////////////////
@has_permission('vendor')
def cms_dashboard(request):
    user = get_cached_user(request, 'vendor')
    context = {
        'cp': 'services',
        'user': user
    }
    return render(request, 'photographer/cms/pages/dashboard.html', context)

@has_permission('vendor')
def cms_reviews(request):
    user = get_cached_user(request, 'vendor')
    services = PhotographerService.objects.only('id', 'vendor', 'category').prefetch_related(
            Prefetch('reviews', queryset=PhotographerReview.objects.order_by('-created_at'))
        ).filter(user=user)
    
    reviews = []
    for service in services:
        slug = (service.vendor.name).lower().replace(" ", "-")
        slug = re.sub(r'[^\w-]', '', slug)
        for review in service.reviews.all():
            review.service.id = service.id
            # Remove all the special characters except hyphens
            review.service.slug = slug
            review.service.category = service.category
            reviews.append(review)
            
    context = {
        'cp': 'services',
        'reviews': reviews,
        'user': user
    }
    return render(request, 'photographer/cms/pages/reviews.html', context)

@has_permission('vendor')
def cms_settings(request):
    user = get_cached_user(request, 'vendor')
    context = {
        'cp': 'services',
        'user': user
    }
    return render(request, 'photographer/cms/pages/settings.html', context)

def category_form_fields(request, category, other):
    if category.lower() == "wedding":
        other['serviceDetails']['offerPreWedding'] = request.POST.get('offerPreWedding', '') 
        other['serviceDetails']['specializedIn'] = request.POST.get('specializedIn', '') 
        other['serviceDetails']['noOfPhotos'] = request.POST.get('noOfPhotos', '') 
        other['serviceDetails']['provideAlbum'] = request.POST.get('provideAlbum', '') 
        other['serviceDetails']['estimatedDeliveryTime'] = request.POST.get('estimatedDeliveryTime', '') 
        other['serviceDetails']['coverMultipleEvents'] = request.POST.get('coverMultipleEvents', '') 
        other['serviceDetails']['offerVideography'] = request.POST.get('offerVideography', '') 
        other['serviceDetails']['serviceVideoCost'] = request.POST.get('serviceVideoCost', "") 
        other['serviceDetails']['serviceVideoCostUnit'] = request.POST.get('serviceVideoCostUnit', '') 
        other['serviceDetails']['chargeExtraForDestinationWeddings'] = request.POST.get('chargeExtraForDestinationWeddings', '') 

    if category.lower() == "baby":
        other['serviceDetails']['providePropsAndOutfits'] = request.POST.get('providePropsAndOutfits', '') 
        other['serviceDetails']['sessionDuration'] = request.POST.get('sessionDuration', '') 
        other['serviceDetails']['includeParentsAndSiblings'] = request.POST.get('includeParentsAndSiblings', '') 
        other['serviceDetails']['requiredSetupOrLocation'] = request.POST.get('requiredSetupOrLocation', '') 
        other['serviceDetails']['safetyMeasures'] = request.POST.get('safetyMeasures', '') 
        other['serviceDetails']['offerThemedPhotoshoots'] = request.POST.get('offerThemedPhotoshoots', '') 
        other['serviceDetails']['expectedTurnaroundTime'] = request.POST.get('expectedTurnaroundTime', '')
        other['serviceDetails']['policyForRescheduling'] = request.POST.getlist('policyForRescheduling', [])
        other['serviceDetails']['provideRawImages'] = request.POST.get('provideRawImages', '')
        other['serviceDetails']['travelCharges'] = request.POST.get('travelCharges', '')

    if category.lower() == "birthday":
        other['serviceDetails']['specializedAgeGroups'] = request.POST.get('specializedAgeGroups', '') 
        other['serviceDetails']['offerThemedShoot'] = request.POST.get('offerThemedShoot', '')
        other['serviceDetails']['inHouseStudio'] = request.POST.get('inHouseStudio', '')
        other['serviceDetails']['chargeExtraForAdditionalHours'] = request.POST.get('chargeExtraForAdditionalHours', '')
        other['serviceDetails']['specialRequests'] = request.POST.get('specialRequests', '')
        other['serviceDetails']['propsOrSetups'] = request.POST.get('propsOrSetups', '')
        other['serviceDetails']['noOfEditedPhotos'] = request.POST.get('noOfEditedPhotos', '')
        other['serviceDetails']['sameDayEditing'] = request.POST.get('sameDayEditing', '')

    if category.lower() == "fashion":
        other['serviceDetails']['specializedIn'] = request.POST.get('specializedIn', '') 
        other['serviceDetails']['noOfLooksCoved'] = request.POST.get('noOfLooksCoved', '') 
        other['serviceDetails']['provideStylists'] = request.POST.get('provideStylists', '') 
        other['serviceDetails']['inHouseStudio'] = request.POST.get('inHouseStudio', '') 
        other['serviceDetails']['providesTeamForMakeup'] = request.POST.get('providesTeamForMakeup', '') 
        other['serviceDetails']['standardTurnaroundTime'] = request.POST.get('standardTurnaroundTime', '') 
        other['serviceDetails']['offerOutdoorFashion'] = request.POST.get('offerOutdoorFashion', '') 
        other['serviceDetails']['provideHighEndRetouch'] = request.POST.get('provideHighEndRetouch', "") 
        other['serviceDetails']['pricingStructure'] = request.POST.get('pricingStructure', '') 
        other['serviceDetails']['offerBulkDiscount'] = request.POST.get('offerBulkDiscount', '')

    if category.lower() == "food":
        other['serviceDetails']['specializedIn'] = request.POST.get('specializedIn', '')
        other['serviceDetails']['propsOrBackdrops'] = request.POST.get('propsOrBackdrops', '')
        other['serviceDetails']['noOfdishesOrSetup'] = request.POST.get('noOfdishesOrSetup', '')
        other['serviceDetails']['startingPricePerDish'] = request.POST.get('startingPricePerDish', '')
        other['serviceDetails']['collaborateWithFoodStylists'] = request.POST.get('collaborateWithFoodStylists', '')
        other['serviceDetails']['offerOnLocationShoots'] = request.POST.get('offerOnLocationShoots', '')
        other['serviceDetails']['lifestyleOrAction'] = request.POST.get('lifestyleOrAction', '')
        other['serviceDetails']['turnaroundTimeForFinalImages'] = request.POST.get('turnaroundTimeForFinalImages', '')
        other['serviceDetails']['editingAndRetouchingIncluded'] = request.POST.get('editingAndRetouchingIncluded', '')
        other['serviceDetails']['promotionalVideos'] = request.POST.get('promotionalVideos', '')

    if category.lower() == "portrait":
        other['serviceDetails']['sessionDuration'] = request.POST.get('sessionDuration', '')
        other['serviceDetails']['noOfEditedPortraits'] = request.POST.get('noOfEditedPortraits', '')
        other['serviceDetails']['allowMultipleOutfits'] = request.POST.get('allowMultipleOutfits', '')
        other['serviceDetails']['provideLocationSuggestions'] = request.POST.get('provideLocationSuggestions', '')
        other['serviceDetails']['inHouseStudio'] = request.POST.get('inHouseStudio', '')
        other['serviceDetails']['provideBasicOrAdvancedRetouching'] = request.POST.get('provideBasicOrAdvancedRetouching', '')
        other['serviceDetails']['propsIncluded'] = request.POST.get('propsIncluded', '')
        other['serviceDetails']['offerFamilyOrGroupPortraitSessions'] = request.POST.get('offerFamilyOrGroupPortraitSessions', '')
        other['serviceDetails']['estimatedDeliveryTime'] = request.POST.get('estimatedDeliveryTime', '')
        other['serviceDetails']['ownPropsOrIdeas'] = request.POST.get('ownPropsOrIdeas', '')

    if category.lower() == "product":
        other['serviceDetails']['photographyTypesOffered'] = request.POST.getlist('photographyTypesOffered', [])
        other['serviceDetails']['haveDedicatedStudio'] = request.POST.get('haveDedicatedStudio', '')
        other['serviceDetails']['equipmentOrSetup'] = request.POST.get('equipmentOrSetup', '')
        other['serviceDetails']['canHandleLargeVolumes'] = request.POST.get('canHandleLargeVolumes', '')
        other['serviceDetails']['servicePriceUnit'] = request.POST.get('servicePriceUnit', '')
        other['serviceDetails']['propsOrBackground'] = request.POST.get('propsOrBackground', '')
        other['serviceDetails']['deliverEditedImages'] = request.POST.get('deliverEditedImages', '')
        other['serviceDetails']['experiencedProductCategories'] = request.POST.get('experiencedProductCategories', '')
        other['serviceDetails']['provideRawImages'] = request.POST.get('provideRawImages', '')
    
    if category.lower() == "maternity":
        other['serviceDetails']['haveSpecificThemes'] = request.POST.get('haveSpecificThemes', '')
        other['serviceDetails']['recommendLocation'] = request.POST.get('recommendLocation', '')
        other['serviceDetails']['provideWardrobeOptions'] = request.POST.get('provideWardrobeOptions', '')
        other['serviceDetails']['privacyAndComfort'] = request.POST.get('privacyAndComfort', '')
        other['serviceDetails']['offerCoupleOrFamily'] = request.POST.get('offerCoupleOrFamily', '')
        other['serviceDetails']['bestTimeForShoot'] = request.POST.get('bestTimeForShoot', '')
        other['serviceDetails']['openToOutdoorOrIndoorSetups'] = request.POST.get('openToOutdoorOrIndoorSetups', '')
        other['serviceDetails']['noOfimagesIncluded'] = request.POST.get('noOfimagesIncluded', "")
        other['serviceDetails']['customProps'] = request.POST.get('customProps', "")
        other['serviceDetails']['clientRequestEditingStyles'] = request.POST.get('clientRequestEditingStyles', "")

    return other

def normalize_date(input_date):
    accepted_formats = ["%Y-%m", "%m/%Y"]  # Accepted date formats

    if input_date:
        for fmt in accepted_formats:
            try:
                # Try to parse the input date with each format
                date_obj = datetime.strptime(input_date, fmt)
                # Convert it to the standard format
                formatted_date = date_obj.strftime("%Y-%m-%d")
                return formatted_date
            except ValueError:
                continue  # Continue to the next format

    # If no formats match, use today's date
    today = date.today()
    formatted_date = today.strftime("%Y-%m-%d")
    return formatted_date

@has_permission('vendor') 
def cms_create(request):
    user = get_cached_user(request, 'vendor')
    if request.method == 'POST' and 'createOrUpdateForm' in request.POST:
        vendor_id = request.POST.get('vendor_id', '')
        vendor_name = request.POST.get('vendor_name', '')
        if vendor_name:
            vendor_name = vendor_name.lower().replace(" ", "-")

        category = request.POST.get('category', '')
        price = request.POST.get('serviceCost', "")
        price_unit = request.POST.get('serviceCostPer', '')
        description = request.POST.get('description', '')
        thumbnail = request.FILES.get('thumbnail', None)
        startedIn = request.POST.get('startedIn', '')
        contact = request.POST.get('pointOfContact', 0)

        formatted_date = normalize_date(startedIn)

        policy = {
            "userCancelPolicy": request.POST.get('userCancelPolicy', ''),
            'vendorCancelPolicy': request.POST.get('vendorCancelPolicy', ''),
            'paymentTerms': request.POST.get('paymentTerms', ''),   
            'termsAndConditions': request.POST.get('termsAndConditions', ''),
        }

        other = {"serviceDetails": {}}
    
        # Get checkbox values
        other['serviceDetails']['includedInPackage'] = request.POST.getlist('includedInPackage', [])
        # Get radio button values
        other['serviceDetails']['customizedPackages'] = request.POST.get('customizedPackages', '')
        other['serviceDetails']['expressDelivery'] = request.POST.get('expressDelivery', '')

        # Travel Info
        other['serviceDetails']['canTravel'] = request.POST.get('canTravel', '')
        other['serviceDetails']['travelOrAccommodation'] = request.POST.get('travelOrAccommodation', '')
        other['serviceDetails']['citiesCovered'] = request.POST.get('citiesCovered', '')
        
        # Packages
        packages = []
        for i in range(len(request.POST.getlist('packageName', []))):  # Iterate over each title
            package_name = request.POST.getlist('packageName', "")[i]
            if package_name:
                package_data = {
                    'name': package_name, 
                    'price': request.POST.getlist('packagePrice')[i],
                    'priceUnit': request.POST.getlist('packagePriceUnit')[i],
                    'details': request.POST.getlist('packageDetails')[i],
                }
                packages.append(package_data)

        other['packages'] = packages
        
        # Add-ons
        addOns = []
        for i in range(len(request.POST.getlist('addOnName', []))):  # Iterate over each title
            addOn_name = request.POST.getlist('addOnName')[i]
            if addOn_name:
                addOn_data = {
                    'name': addOn_name,
                    'price': request.POST.getlist('addOnPrice')[i],
                    'priceUnit': request.POST.getlist('addOnPriceUnit')[i],
                    'details': request.POST.getlist('addOnDetails')[i],
                }
                addOns.append(addOn_data) 

        other['addOns'] = addOns

        if thumbnail and thumbnail is not None:
            thumbnail.name = f"{category}-photography-eventic-{str(uuid4())[:8]}.{thumbnail.name.split('.')[-1]}"

        service_detail = PhotographerService.objects.create(
            vendor_id=vendor_id, 
            user=user, 
            category=category, 
            price=price,
            price_unit=price_unit, 
            description=description, 
            contact=contact,
            thumbnail=thumbnail,
            policy=policy,
            other=category_form_fields(request, category, other),
            experience=formatted_date
        )

        content_type = ContentType.objects.get_for_model(PhotographerService)
        VendorService.objects.create(vendor_id=vendor_id, content_type=content_type, object_id=service_detail.id)

        # Add images to gallery
        image_files = request.FILES.getlist('imageFile', [])
        image_descriptions = request.POST.getlist('imageDescription', [])

        if image_files and image_descriptions:
            content_type = ContentType.objects.get_for_model(PhotographerGallery)

            # Prepare lists for bulk creation
            photographer_gallery_instances = []
            vendor_gallery_instances = []

            # Loop through images and prepare instances
            for i, image in enumerate(image_files):
                if image:
                    description = image_descriptions[i] if i < len(image_descriptions) else ''
                    image.name = f"{category}-photography-eventic-{str(uuid4())[:8]}.{image.name.split('.')[-1]}"
                    
                    # Create PhotographerGallery instance
                    photographer_gallery = PhotographerGallery(
                        service_id=service_detail.id,
                        vendor_id=vendor_id,
                        image=image,
                        description=description
                    )
                    photographer_gallery_instances.append(photographer_gallery)

            # Bulk create PhotographerGallery instances
            photographer_gallery_objects = PhotographerGallery.objects.bulk_create(photographer_gallery_instances)

            # Prepare VendorGallery instances after PhotographerGallery instances are saved
            for pg_instance in photographer_gallery_objects:
                vendor_gallery = VendorGallery(
                    vendor_id=vendor_id,
                    content_type=content_type,
                    object_id=pg_instance.id
                )
                vendor_gallery_instances.append(vendor_gallery)

            # Bulk create VendorGallery instances
            VendorGallery.objects.bulk_create(vendor_gallery_instances)
            
        cache_keys_to_delete = [f'vendor_services_{user.id}', f'services_list_{user.id}', f'services_app_list_{user.id}']
        for key in cache_keys_to_delete:
            cache.delete(key)

        messages.success(request, "Service has been created successfully.")
        return redirect('vendor:Services')
    
    vendor = Vendor.objects.get(user=user)
    vendor_photography_services = PhotographerService.objects.only('id', 'category').filter(vendor_id=vendor.id)

    available_categories = []
    vendor_photography_categories = {}
    for key, value in photographer_services['photographer'].items():
        if not vendor_photography_services.filter(category=key).exists() and value['active']:
            available_categories.append(key)
            vendor_photography_categories[key] = value

    category = request.GET.get('category', '')
    category_form_template = ""
    if category:
        # check if category exists in available_categories
        if category in available_categories:
            # Get the rendered form component
            team_members = TeamMember.objects.filter(vendor_id=vendor.id)
            template_name = photographer_services['photographer'].get(category)['template']
            rendered_form_component = render(request, f"photographer/cms/category_forms/{template_name}.html", {'cp': 'create', 'teamMembers': team_members}).content.decode('utf-8')
            category_form_template = rendered_form_component

    context = {
        'cp': 'services',
        'page': 'create',
        'vendor': vendor,
        'user': user,
        'rendered_form': category_form_template,
        'category': category,
        'vendor_photography_categories': vendor_photography_categories
    }
    return render(request, 'photographer/cms/pages/create-or-update.html', context)

@has_permission('vendor')
def cms_update(request, id):
    user = get_cached_user(request, 'vendor')
    if request.method == 'POST' and 'createOrUpdateForm' in request.POST:
        service = get_object_or_404(PhotographerService, id=id)
        service.price = request.POST.get('serviceCost', "")
        service.price_unit = request.POST.get('serviceCostPer', '')
        service.description = request.POST.get('description', '')
        startedIn = request.POST.get('startedIn', '')
        service.is_active = request.POST.get('is_active', '') == 'on'
        service.contact = request.POST.get('pointOfContact', 0)

        formatted_date = normalize_date(startedIn)

        service.experience = formatted_date
        
        service.policy = {
            "userCancelPolicy": request.POST.get('userCancelPolicy', ''),
            'vendorCancelPolicy': request.POST.get('vendorCancelPolicy', ''),
            'paymentTerms': request.POST.get('paymentTerms', ''),   
            'termsAndConditions': request.POST.get('termsAndConditions', ''),
        }

        other = {"serviceDetails": {}}
    
        # Get checkbox values
        other['serviceDetails']['includedInPackage'] = request.POST.getlist('includedInPackage', [])
        # Get radio button values
        other['serviceDetails']['customizedPackages'] = request.POST.get('customizedPackages', '')
        other['serviceDetails']['expressDelivery'] = request.POST.get('expressDelivery', '')

        # Travel Info
        other['serviceDetails']['canTravel'] = request.POST.get('canTravel', '')
        other['serviceDetails']['travelOrAccommodation'] = request.POST.get('travelOrAccommodation', '')
        other['serviceDetails']['citiesCovered'] = request.POST.get('citiesCovered', '')
        
        # Packages
        packages = []
        for i in range(len(request.POST.getlist('packageName', []))):  # Iterate over each title
            package_name = request.POST.getlist('packageName', [])[i]
            if package_name:
                package_data = {
                    'name': package_name,
                    'price': request.POST.getlist('packagePrice')[i],
                    'priceUnit': request.POST.getlist('packagePriceUnit')[i],
                    'details': request.POST.getlist('packageDetails')[i],
                }
                packages.append(package_data)

        other['packages'] = packages
        
        # Add-ons
        addOns = []
        for i in range(len(request.POST.getlist('addOnName', []))):  # Iterate over each title
            addOn_name = request.POST.getlist('addOnName')[i]
            if addOn_name:
                addOn_data = {
                    'name': addOn_name,
                    'price': request.POST.getlist('addOnPrice')[i],
                    'priceUnit': request.POST.getlist('addOnPriceUnit')[i],
                    'details': request.POST.getlist('addOnDetails')[i],
                }
                addOns.append(addOn_data) 

        other['addOns'] = addOns

        service.other = category_form_fields(request, service.category, other)
        
        # Update Thumbnail
        thumbnail = request.FILES.get('thumbnail', None)
        file_exists = request.POST.get('file_exists')
        
        if file_exists == "nofile":
            if service.thumbnail and default_storage.exists(service.thumbnail.name):
                default_storage.delete(service.thumbnail.name)
            service.thumbnail = ""

        if file_exists == "changed" and thumbnail:
            if service.thumbnail and default_storage.exists(service.thumbnail.name):
                default_storage.delete(service.thumbnail.name)
            
            category = photographer_services['photographer'].get(service.category)['name'].replace(' ', '-').lower()
            thumbnail.name = f"{category}-photography-eventic-{str(uuid4())[:8]}.{thumbnail.name.split('.')[-1]}"
            service.thumbnail = thumbnail

        service.save()

        # Add images to gallery
        image_files = request.FILES.getlist('imageFile', [])
        image_descriptions = request.POST.getlist('imageDescription', [])

        if image_files and image_descriptions:
            content_type = ContentType.objects.get_for_model(PhotographerGallery)

            # Prepare lists for bulk creation
            photographer_gallery_instances = []
            vendor_gallery_instances = []

            # Loop through images and prepare instances
            for i, image in enumerate(image_files):
                if image:
                    description = image_descriptions[i] if i < len(image_descriptions) else ''
                    image.name = f"{service.category}-photography-eventic-{str(uuid4())}.{image.name.split('.')[-1]}"
                    
                    # Create PhotographerGallery instance
                    photographer_gallery = PhotographerGallery(
                        service_id=service.id,
                        vendor_id=service.vendor.id,
                        image=image,
                        description=description
                    )
                    photographer_gallery_instances.append(photographer_gallery)

            # Bulk create PhotographerGallery instances
            photographer_gallery_objects = PhotographerGallery.objects.bulk_create(photographer_gallery_instances)

            # Prepare VendorGallery instances after PhotographerGallery instances are saved
            for pg_instance in photographer_gallery_objects:
                vendor_gallery = VendorGallery(
                    vendor_id=service.vendor.id,
                    content_type=content_type,
                    object_id=pg_instance.id
                )
                vendor_gallery_instances.append(vendor_gallery)

            # Bulk create VendorGallery instances
            VendorGallery.objects.bulk_create(vendor_gallery_instances)
        
        cache_keys_to_delete = [f'vendor_services_{user.id}', f'services_list_{user.id}', f'services_app_list_{user.id}']
        for key in cache_keys_to_delete:
            cache.delete(key)

        messages.success(request, "Service has been updated successfully.")
        return redirect('vendor:Services')

    service = PhotographerService.objects.select_related('vendor').annotate(gallery_count=Count('gallery', distinct=True)).get(id=id)
    vendor = service.vendor

    team_members = TeamMember.objects.filter(vendor_id=vendor.id)

    experience = service.experience
    if experience:
        # Parse the date string as YYYY-MM-DD
        date_obj = datetime.strptime(str(experience), "%Y-%m-%d")
        # Extract year and month components
        year = date_obj.year
        month = date_obj.month
        # Format the date as YYYY-MM
        service.experience = f"{year}-{month:02d}"
        category_info = photographer_services['photographer'].get(service.category, None)
        if category_info is not None and category_info['active']:
            template = category_info['template']
            rendered_form_component = render(request, f"photographer/cms/category_forms/{template}.html", {'service': service, 'teamMembers': team_members, 'page': 'update'}).content.decode('utf-8')
        else:
            rendered_form_component = ""
        
    context = {
        'cp': 'services',
        'page': 'update',
        'service': service,
        'vendor': vendor,
        'rendered_form': rendered_form_component,
        'user': user
    }
    return render(request, 'photographer/cms/pages/create-or-update.html', context)

@has_permission('vendor')
def cms_load_category_form_component(request):
    user = get_cached_user(request, 'vendor')
    category = request.GET.get('category', '')
    category_data = photographer_services['photographer'].get(category, None)
    rendered_form_component = ""
    if category_data is not None and category_data['active']:
        team_members = TeamMember.objects.filter(vendor_id=user.vendor_id)
        template = category_data['template']
        rendered_form_component = render(request, f"photographer/cms/category_forms/{template}.html", {'cp': 'create', 'teamMembers': team_members}).content.decode('utf-8')

    data = {
        'rendered_form': rendered_form_component,
    }
    return JsonResponse(data)

@has_permission('vendor')
def cms_gallery(request):
    user = get_cached_user(request, 'vendor')
    if request.method == 'POST' and 'add_images' in request.POST:
        service_meta_slug = request.POST.get('service_meta_slug', '')
        
        if service_meta_slug:
            vendor_id = service_meta_slug.split("_")[-1]
            service_id = service_meta_slug.split("_")[-2]
            image_name = service_meta_slug.split("_")[1]
        
        # Retrieve files and descriptions once
        image_files = request.FILES.getlist('imageFile')
        image_descriptions = request.POST.getlist('imageDescription')

        # Get content type once
        content_type = ContentType.objects.get_for_model(PhotographerGallery)

        # Prepare lists for bulk creation
        photographer_gallery_instances = []
        vendor_gallery_instances = []

        # Loop through images and prepare instances
        for i, image in enumerate(image_files):
            if image:
                description = image_descriptions[i] if i < len(image_descriptions) else ''
                
                # Compress image before saving
                image = compress_image(image, quality=30)
                image.name = f"{image_name}-photography-{str(uuid4())[:4]}.{image.name.split('.')[-1]}"
                
                # Create PhotographerGallery instance
                photographer_gallery = PhotographerGallery(
                    service_id=service_id,
                    vendor_id=vendor_id,
                    image=image,
                    description=description
                )
                photographer_gallery_instances.append(photographer_gallery)

        # Bulk create PhotographerGallery instances
        photographer_gallery_objects = PhotographerGallery.objects.bulk_create(photographer_gallery_instances)

        # Prepare VendorGallery instances after PhotographerGallery instances are saved
        for pg_instance in photographer_gallery_objects:
            vendor_gallery = VendorGallery(
                vendor_id=vendor_id,
                content_type=content_type,
                object_id=pg_instance.id
            )
            vendor_gallery_instances.append(vendor_gallery)

        # Bulk create VendorGallery instances
        VendorGallery.objects.bulk_create(vendor_gallery_instances)
        messages.success(request, "Images have been added successfully.")

        return redirect('photographer:Gallery')

    services = PhotographerService.objects.only('id', 'vendor', 'category').prefetch_related(Prefetch('gallery')).filter(user=request.user)
    gallery = []

    vendor = None
    for service in services:
        slug = (service.vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        service.slug = slug
        service.meta_slug = f"{slug}_{service.category}_{str(service.id)}_{service.vendor_id}"

        if vendor != service.vendor:
            vendor = service.vendor

        for image in service.gallery.all():
            gallery.append(image)

    context = {
        'cp': 'services',
        'gallery': gallery,
        'services': services,
        'vendor': vendor,
        'user': user
    }
    return render(request, 'photographer/cms/pages/gallery.html', context)

@has_permission('vendor')
def cms_gallery_delete(request, id):
    # delete image
    image = get_object_or_404(PhotographerGallery, id=id)
    if request.user != image.vendor.user:
        messages.error(request, "You don't have permission to delete this image.")
        return redirect('photographer:Gallery')
    image.delete()
    messages.success(request, "Image has been deleted successfully.")

    return redirect('photographer:Gallery')

@has_permission('vendor')
def cms_delete_service(request):
    if request.method == 'POST' and 'deleteServiceBtn' in request.POST:
        id = request.POST.get('deleteServiceBtn', "")
        if id:
            print(id)
            service = get_object_or_404(PhotographerService, id=id)
            service.delete()
            print(service)
            messages.success(request, "Service has been deleted successfully.")
        else:
            messages.error(request, "Service not found.")

    return redirect('vendor:Services')

#/////////////   Users   //////////////
def home(request):
    return render(request, 'photographer/home.html')

@set_anonymous_user_cookie
def request_callback(request, slug, service_id, vendor_id):
    if request.method == 'POST' and 'request_callback' in request.POST:
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        cookie_uid = request.COOKIES.get('uid') if request.COOKIES.get('uid', None) else  hashlib.md5(f"{get_client_ip(request)}".encode()).hexdigest()

        service = PhotographerService.objects.prefetch_related('vendor', 'user').only('id', 'category', 'contact', 'user__id', 'user__username', 'user__first_name', 'user__last_name', 'vendor__id', 'vendor__email', 'vendor__name').get(pk=service_id)

        email_to = service.vendor.email
        poc = None
        if service.contact:
            poc = TeamMember.objects.get(pk=service.contact)
            email_to = poc.email

        # create callback request
        PhotographerCallbackRequest.objects.create(vendor_id=vendor_id, name=name, email=email, phone=phone, message=message, service_id=service_id, uid=cookie_uid)
        PhotographerLead.objects.create(vendor_id=vendor_id, service_id=service_id, uid=cookie_uid, lead_type='callback_request')

        user_name = f"{service.user.first_name} {service.user.last_name}" if service.user.first_name and service.user.last_name else service.user.username
        cc_emails = [service.vendor.email] if service.vendor.email != email_to else []
        # send callback lead email
        settings.THREAD_POOL_EXECUTOR.submit(
            send_callback_lead_email,
            email_to=email_to,
            cc_emails=cc_emails,
            vendor_name=user_name,
            client_name=name,
        )
        # send callback request notification
        settings.THREAD_POOL_EXECUTOR.submit(
            create_notification, 
            user_id=service.user.id, 
            title="Callback Request", 
            notification_type="callback_request", 
            description=f"Callback Request from {name.title()} for {(service.category).title()} Photographer Service.", 
            other={
                "service_id": service_id,
                "url": f"/photographer/service/{service_id}/{slug}",
                "client_name": name,
                "client_phone": phone,
                "client_email": email,
                "client_message": message
            }
        )
        messages.success(request, "Your request has been submitted successfully.")  

    return redirect('photographer:service', service_id=service_id, slug=slug)


# //////////////////     SERVICE    ///////////////////////////
@login_required(login_url='auth:login')
def service_rating(request):
    if request.method == 'POST' and 'submit_review' in request.POST:
        rating = int(request.POST.get('rating', "1"))
        vendor_id = request.POST.get('vendor_id', "")
        service_id = request.POST.get('service_id', "")
        review = request.POST.get('review', "")
        recommend_for = request.POST.getlist('recommend_for', [])

        uid = str(uuid4())[:8]
        approved = True if int(rating) >= 4 else False
        
        PhotographerReview.objects.create(rating=rating, review=review, vendor_id=vendor_id, recommend_for=recommend_for, uid=uid, user=request.user, service_id=service_id, approved=approved)

        # Clear cache for service details page
        cache_key = f'photographer_service_details_{service_id}'
        cache.delete(cache_key)
        messages.success(request, "Your review has been submitted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))

@login_required(login_url='auth:login')
def report_service(request):
    if request.method == 'POST' and 'report_service' in request.POST:
        service_id = request.POST.get('service_id', "")
        reason = request.POST.get('report_reason', "")
        description = request.POST.get('report_description', "")
        screenshot = request.FILES.get('screenshot', None)
        # chenge the screenshot name to be unique with uuid and add the extension
        if screenshot:
            screenshot.name = str(uuid4()) + '.' + screenshot.name.split('.')[-1]

        uid = str(uuid4())[:8]
        ReportPhotographerService.objects.create(service_id=service_id, uid=uid, screenshot=screenshot, reason=reason, description=description, user=request.user)
        messages.success(request, "Your report has been submitted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))

@login_required(login_url='auth:login')
def report_review(request):
    if request.method == 'POST' and 'report_review' in request.POST:
        review_id = request.POST.get('review_id', "")
        reason = request.POST.get('report_reason', "")
        uid = str(uuid4())[:8]
        ReportPhotographerReview.objects.create(review_id=review_id, uid=uid, reason=reason, user=request.user)
        messages.success(request, "Your report has been submitted successfully.")
    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))

@login_required(login_url='auth:login')
def delete_review(request):
    if request.method == 'POST' and 'delete_review' in request.POST:
        review_id = request.POST.get('review_id')
        review = get_object_or_404(PhotographerReview, id=review_id, user=request.user)
        id = review.service_id
        review.delete()
        cache_key = f'photographer_service_details_{id}'
        cache.delete(cache_key)
        messages.success(request, "Your review has been deleted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))


# ////////////////    SEARCH    ///////////////////////
def search_by_service(request):
    return search(request, category=None)

def search(request, category):
    user = get_cached_user(request)
    query = request.GET.get('q', '')

    _results = search_with_ranking(query, category)
    services = []
    ad_active = []
    for result in _results['results']:
        result.category = result.category.replace("_", " ")
        if result.ad_active:
            ad_active.append(result)
        else:
            services.append(result)

    random.shuffle(services)

    results = ad_active + services
    vendor_service = f'{category.replace("_", " ")} ' if category and category is not None else ""

    # Select one random title
    title = random.choice(_results['titles'])
    meta_description = _results['meta_description']
    meta_keywords = _results['meta_keywords']

    data = {
        'query': query,
        'results': results,
        'eventron_service':  f'{vendor_service} Photographer',
        'user': user,
        'title': title,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords
    }
    return render(request, "photographer/pages/search.html", data)


def search_with_ranking_and_titles(search_string, category):
    """
    Searches for photographers and generates SEO-friendly titles based on matches.

    Args:
        search_string: The string containing words to search for.
        category: The category of services to filter by.

    Returns:
        A dictionary containing:
            - results: The search results queryset.
            - titles: A list of SEO-friendly titles based on search matches.
    """
    stopwords = [
        "i", "me", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs", "what", "which", "that", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "been", "has", "have", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "or", "for", "nor", "so", "yet", "because", "near",
        "at", "by", "in", "into", "of", "on", "to", "with", "around",
        "as", "has", "have", "had", "having", "be", "s", "t", "can", "must", "will", "may", "might", "shall", "should", "would",
        "not", "no",
        "up", "down", "left", "right", "all", "any", "both", "each", "few", "more", "most", "some", "such", "other", "another",
        "very", "most", "only", "just", "too", "well", "also", "still", "even", "always",
        "photographer", "photographers", "photography", "photo", "photos",
    ]

    special_characters = ["#", "$", "%", "&", "?", ".", ",", "!", ":", ";", '"', "'", "`", "-", "=", "+", "*", "/", "|", "^", "(", ")", "[", "]", "{", "}"]

    # Preprocess search string
    words = search_string.lower().split() if search_string.strip() else []
    prioritized_matches = {}
    titles = []

    # Build prioritized conditions
    prioritized_conditions = Q()
    for word in words:
        if word not in stopwords and word not in special_characters:
            prioritized_conditions |= (
                Q(vendor__name__icontains=word) |
                Q(vendor__address__icontains=word) |
                Q(vendor__city__icontains=word) |
                Q(vendor__state__icontains=word) |
                Q(vendor__pincode__icontains=word)
            )

            # Track matches
            prioritized_matches[word] = []
            if PhotographerService.objects.filter(Q(vendor__city__icontains=word)).exists():
                prioritized_matches[word].append("city")
            if PhotographerService.objects.filter(Q(vendor__name__icontains=word)).exists():
                prioritized_matches[word].append("vendor name")
            if PhotographerService.objects.filter(Q(vendor__address__icontains=word)).exists():
                prioritized_matches[word].append("address")
            if PhotographerService.objects.filter(Q(vendor__state__icontains=word)).exists():
                prioritized_matches[word].append("state")
            if PhotographerService.objects.filter(Q(vendor__pincode__icontains=word)).exists():
                prioritized_matches[word].append("pincode")

    # Filter results    if category is None:
    categories = [category['category'] for category in photographer_services['photographer'].values() if category['active']]

    matching_category = next((word for word in words if word in categories), None)
    if matching_category:
        category = matching_category

    conditions = Q(vendor__is_active=True) & Q(is_active=True)
    if category:
        conditions &= Q(category__icontains=category)
    if prioritized_conditions:
        conditions &= prioritized_conditions

    results = (
        PhotographerService.objects
        .select_related('vendor')
        .only('thumbnail', 'category', 'vendor__name', 'vendor__address', 'vendor__city', 'vendor__state', 'vendor__pincode', 'vendor__is_verified', 'vendor', 'other', 'experience', 'price', 'price_unit', 'is_verified', 'ad_active', 'sponsorship_active')
        .filter(conditions)
    )

    for result in results:
        if result.thumbnail and default_storage.exists(result.thumbnail.name):
            result.has_thumbnail = True
        
        slug = (result.vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        result.slug = slug

    # Add SEO titles based on matches
    for word, fields in prioritized_matches.items():
        category = f" {category.capitalize()}" if category is not None else ""
        results_count = f"{len(results)} " if results else ""
        if "city" in fields:
            titles.append(f"{results_count}Best{category} Photographers in {word.capitalize()}")
        if "vendor name" in fields:
            titles.append(f"Hire {word.capitalize()}, the Top-rated{category} Photographer")
        if "address" in fields:
            titles.append(f"Discover the Best{category} Photographers Near {word.capitalize()}")
        if "state" in fields:
            titles.append(f"Top-rated{category} Photographers in {word.capitalize()} State")
        if "pincode" in fields:
            titles.append(f"Find Top-rated{category} Photographers in Pincode {word}")

    
    # Add SEO titles based on matches
    for word, fields in prioritized_matches.items():
        if "city" in fields and "state" in fields:
            titles.append(f"13 Best {category.capitalize()} Photographers in {word.capitalize()}, {word.capitalize()} State")
        elif "city" in fields:
            titles.append(f"13 Best {category.capitalize()} Photographers in {word.capitalize()}")
        elif "vendor name" in fields:
            titles.append(f"Hire {word.capitalize()}, the Top-rated {category.capitalize()} Photographer")
        elif "address" in fields:
            titles.append(f"Discover the Best {category.capitalize()} Photographers Near {word.capitalize()}")
        elif "pincode" in fields:
            titles.append(f"Find {category.capitalize()} Photographers in Pincode {word}")

    # Create meta description
    if titles:
        meta_description = f"Looking for the best {category} photographers? {titles[0]}. Explore more top-rated photographers now!"
    else:
        meta_description = f"Find the best {category} photographers for your needs. Top-rated, experienced, and highly recommended professionals available."

    # Generate keywords
    keywords = set()
    for result in results:
        keywords.update([
            result.vendor.name,
            result.vendor.city,
            result.vendor.state,
            result.category,
        ])
    keywords = [k for k in keywords if k and k.lower() not in stopwords][:15]
    meta_keywords = ', '.join(keywords)

    if not titles:
        category = f"{category.capitalize()} " if category is not None else ""
        titles.append(f"Discover the Best {category.capitalize()}Photographers")

    # Randomize the order of results
    results = list(results)
    random.shuffle(results)

    return {"results": results, "titles": titles, "meta_description": meta_description, "meta_keywords": meta_keywords}

def search_with_ranking(search_string, category):
    """
    Searches for photographers and generates SEO-friendly titles based on matches.

    Args:
        search_string: The string containing words to search for.
        category: The category of services to filter by.

    Returns:
        A dictionary containing:
            - results: The search results queryset.
            - titles: A list of SEO-friendly titles based on search matches.
    """
    stopwords = [
        "i", "me", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs", "what", "which", "that", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "been", "has", "have", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "or", "for", "nor", "so", "yet", "because", "near",
        "at", "by", "in", "into", "of", "on", "to", "with", "around",
        "as", "has", "have", "had", "having", "be", "s", "t", "can", "must", "will", "may", "might", "shall", "should", "would",
        "not", "no",
        "up", "down", "left", "right", "all", "any", "both", "each", "few", "more", "most", "some", "such", "other", "another",
        "very", "most", "only", "just", "too", "well", "also", "still", "even", "always",
        "photographer", "photographers", "photography", "photo", "photos",
    ]

    special_characters = ["#", "$", "%", "&", "?", ".", ",", "!", ":", ";", '"', "'", "`", "-", "=", "+", "*", "/", "|", "^", "(", ")", "[", "]", "{", "}"]

    categories = [category['category'] for category in photographer_services['photographer'].values() if category['active']]

    search_ignored = stopwords + special_characters
    words = search_string.lower().split() if search_string.strip() else []

    if category is None:
        matching_category = next((word for word in words if word in categories), None)
        if matching_category:
            category = matching_category

    conditions = Q(vendor__is_active=True) & Q(is_active=True)
    if category:
        conditions &= Q(category__icontains=category)

    # Add conditions for prioritized and secondary searches
    prioritized_conditions = Q()
    secondary_conditions = Q()

    for word in words:
        if word not in search_ignored:
            prioritized_conditions |= (
                Q(vendor__name__icontains=word) |
                Q(vendor__address__icontains=word) |
                Q(vendor__city__icontains=word) |
                Q(vendor__state__icontains=word) |
                Q(vendor__pincode__icontains=word)
            )
            secondary_conditions |= Q(other__icontains=word)

    if prioritized_conditions or secondary_conditions:
        conditions &= (prioritized_conditions | secondary_conditions)

    # Avoid empty Q() in When() conditions
    when_conditions = []
    if prioritized_conditions:
        when_conditions.append(When(prioritized_conditions, then=Value(1)))
    if secondary_conditions:
        when_conditions.append(When(secondary_conditions, then=Value(2)))

    results = (
        PhotographerService.objects
        .select_related('vendor')
        .only(
            'thumbnail', 'category', 'vendor__name', 'vendor__address', 'vendor__city', 'vendor__state',
            'vendor__pincode', 'vendor__is_verified', 'vendor', 'other', 'experience', 'price', 
            'price_unit', 'is_verified', 'ad_active', 'sponsorship_active'
        )
        .filter(conditions)
        .annotate(
            rank=Case(
                *when_conditions,  # Add conditions dynamically
                default=Value(3),
                output_field=IntegerField()
            )
        )
        .order_by('rank')  # Prioritize by rank
    )

    # Add slug and check thumbnail existence
    for result in results:
        if result.thumbnail and default_storage.exists(result.thumbnail.name):
            result.has_thumbnail = True

        slug = (result.vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        result.slug = slug

    # Generate SEO titles, meta description, and keywords
    matches = {"city": None, "state": None, "vendor_name": None, "address": None}
    for word in words:
        for result in results:
            if word in (result.vendor.city or "").lower():
                matches["city"] = word
            if word in (result.vendor.state or "").lower():
                matches["state"] = word
            if word in (result.vendor.name or "").lower():
                matches["vendor_name"] = word
            if word in (result.vendor.address or "").lower():
                matches["address"] = word

    # Generate titles
    titles = []
    _category = f"{category.capitalize()} " if category is not None else ""
    results_count = f"{len(results)} " if results else ""
    if matches["city"] and matches["state"]:
        titles.append(f"{results_count}Best {_category}Photographers in {matches['city'].capitalize()}, {matches['state'].capitalize()}")
    elif matches["city"]:
        titles.append(f"{results_count}Best {_category}Photographers in {matches['city'].capitalize()}")
    elif matches["state"]:
        titles.append(f"Top {_category}Photographers in {matches['state'].capitalize()}")
    elif matches["vendor_name"]:
        titles.append(f"Discover the Best {_category}Photographers like {matches['vendor_name'].capitalize()}")
    elif matches["address"]:
        titles.append(f"Find the Top {_category}Photographers Near {matches['address'].capitalize()}")
    else:
        titles.append(f"Find the Best {_category}Photographers Near You")

    # Generate meta description
    meta_description = f"Explore the best {_category}photographers in {matches['city'] or matches['state'] or 'your area'}. Book top-rated professionals today!"

    # Generate meta keywords
    meta_keywords = set()
    for result in results:
        if result.vendor.city:
            meta_keywords.add(result.vendor.city.lower())
        if result.vendor.state:
            meta_keywords.add(result.vendor.state.lower())
        if result.category:
            meta_keywords.add(result.category.lower())
    meta_keywords = list(meta_keywords)[:20] if len(meta_keywords) > 20 else list(meta_keywords) # Limit to 15 keywords

    return {
        "results": list(results),
        "titles": titles,
        "meta_description": meta_description,
        "meta_keywords": meta_keywords
    }



@set_anonymous_user_cookie
def service_details(request, service_id, slug):
    user = get_cached_user(request)
    cookie_uid = hashlib.md5(f"user-{user.id}".encode()).hexdigest() if user.is_authenticated else request.COOKIES.get('uid')
    
    if request.method == 'POST' and 'lead' in request.POST:
        lead_type = request.POST.get('lead_type', '')
        # Check if user lead limit is exceeded
        today = date.today()

        if UserLead.objects.filter(created_at__date=today, uid=cookie_uid).count() >= 50:
            data = {
                'error': True,
                'message': 'You have reached the limit of 5 leads per day. Please try again tomorrow.'
            }
            return JsonResponse(data, status=200, safe=False)
            
        service = PhotographerService.objects.only('id', "vendor__id", 'contact').get(id=service_id)
        # create lead
        PhotographerLead.objects.create(
            service_id=service_id,
            vendor_id=service.vendor.id,
            lead_type = lead_type,
            uid = cookie_uid
        )

        poc = None
        if service.contact:
            poc = TeamMember.objects.get(pk=service.contact)

        action = ''
        if lead_type == 'phone':
            action = f"tel:+91{service.vendor.phone}" if poc is None else f'tel:+91{poc.phone}'
        elif lead_type == 'email':
            action = f"mailto:{service.vendor.email}" if poc is None else f'mailto:{poc.email}'
        elif lead_type == 'whatsapp':
            action = f"https://wa.me/91{service.vendor.phone}" if poc is None else f'https://wa.me/91{poc.whatsapp}'

        data = {
            'action': action,
            'error': False
        }
        return JsonResponse(data, status=200, safe=False)

    # Define a unique cache key based on service ID
    # cache_key = f'photographer_service_details_{id}'
    # _service = cache.get(cache_key)
    _service = False

    if not _service:
        # Today's date and user's IP address
        today = date.today()

        # Base query with all necessary prefetches and filters
        try:
            reviews_conditions = Q(approved=True)
            if user.is_authenticated:
                reviews_conditions |= Q(user=request.user)

            # Adjust this subquery to count `UserLead` objects for a given user and day, independent of service
            todays_user_leads = UserLead.objects.filter(
                created_at__date=today,  # Filters by the date portion only
                uid=cookie_uid,
            ).count()  # `total_leads` counts today's leads per user

            conditions = Q(vendor__is_active=True) & Q(is_active=True)

            _service = PhotographerService.objects.select_related('vendor').prefetch_related(
                Prefetch('gallery'),
                Prefetch('reviews', queryset=PhotographerReview.objects.filter(reviews_conditions).order_by('-created_at')),
            ).annotate(
                total_leads=Count('leads', filter=Q(leads__created_at__gte=today - timedelta(days=30)), distinct=True),
                like_count=Count('likes', distinct=True),
                has_user_lead=Exists(
                    PhotographerLead.objects.filter(
                        created_at__date=today,
                        lead_type='callback_request',
                        uid=cookie_uid,
                        service_id=OuterRef('pk')
                    )
                ),
                has_gallery=Exists(
                    PhotographerService.objects.filter(
                        gallery__image__isnull=False,
                        gallery__image__gt='',  # Check if image field is not empty
                        id=OuterRef('pk')
                    )
                ),
                reviews_count=Count('reviews', 
                                    filter=Q(reviews__approved=True) | Q(reviews__user=user) if user.is_authenticated else Q(reviews__approved=True), 
                                    distinct=True),
                has_rated = Exists(
                    PhotographerReview.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False),
                is_liked=Exists(
                    PhotographerLike.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False),
                is_saved=Exists(
                    PhotographerSave.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False)
            ).only(
                'id', 'category', 'description', 'price', 'price_unit', 'other', 'thumbnail', 'experience', 'vendor',
                'vendor__id', 'vendor__name', 'vendor__opening_time', 'vendor__closing_time', 'vendor__email', 'vendor__phone', 'vendor__whatsapp', 'vendor__bio',
                'vendor__address', 'vendor__city', 'vendor__state', 'vendor__country', 'vendor__pincode', 
                'vendor__website', 'vendor__facebook', 'vendor__instagram', 'vendor__twitter',
                'leads', 'leads__id', 'leads__uid', 'leads__lead_type', 'leads__created_at',
                'gallery', 'gallery__image',
            ).filter(conditions).get(id=service_id)

        except PhotographerService.DoesNotExist:
            messages.error(request, "(｡•́︿•̀｡) Service does not exist.")
            return redirect('photographer:search_service')
        
        # If todays_user_leads is gt_then or equal to 5, set user_can_contact to False
        _service.user_allowed_to_contact = True if todays_user_leads < 200 else False
        category = photographer_services['photographer'].get(_service.category, _service.category)

        # Additional flags based on the 'other' JSONField
        other_data = _service.other or {}
        _service.has_packages = True if other_data.get('packages', {}) else False 
        _service.has_addOns = True if other_data.get('addOns', {}) else False
        _service.has_faqs = True if other_data.get('faqs', {}) else False

        # Check if the service thumbnail exists
        _service.has_thumbnail = bool(_service.thumbnail and default_storage.exists(_service.thumbnail.name))

        # Get the content type for the service
        _service.content_type = ContentType.objects.get_for_model(_service)
        _service.slug = slug

        # Store the service details in cache

        show_gallery = []
        image_gallery = []

        for image in _service.gallery.all():
            if image.image and default_storage.exists(image.image.name):
                image.has_image = True
                show_gallery.append(image)
                image_gallery.append(image)
            else:
                image.has_image = False

        # Get 5 random images from the show gallery
        _service.show_gallery = random.sample(show_gallery, 5) if len(show_gallery) > 5 else show_gallery

        # Randomize the order of the gallery
        random.shuffle(image_gallery)
        image_gallery_count = len(image_gallery) - 4

        user_can_call = False
        opening_time = _service.vendor.opening_time
        closing_time = _service.vendor.closing_time

        if opening_time and closing_time:
            # Convert the opening and closing times to datetime objects
            opening_time = datetime.strptime(str(opening_time), "%H:%M:%S").strftime("%H:%M")
            closing_time = datetime.strptime(str(closing_time), "%H:%M:%S").strftime("%H:%M")

            # Check if the current time is between the opening and closing times
            current_time = datetime.now().time().strftime("%H:%M")

            if opening_time <= current_time <= closing_time:
                user_can_call = True
            else:
                user_can_call = False

        _service.user_can_call = user_can_call

    # Prepare the context and render the response
    context = {
        'service': _service,
        'category': category,
        'user': user,
        'image_gallery': image_gallery,
        'image_gallery_count': image_gallery_count
    }
    return render(request, 'photographer/pages/details.html', context)

@login_required
def toggle_like(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        service_id = request.POST.get('service_id')
        user_id = request.user.id

        # Call the like_object function to like the object
        liked = like_object(user_id, service_id, vendor_id)
        
        cache_key = f'photographer_service_details_{service_id}'
        cache.delete(cache_key)

    # Return JSON response with the new like state
    data = {'liked': liked}
    return JsonResponse(data, status=200, safe=False)
    # return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))

def like_object(user_id, service_id, vendor_id):
    """
    Add a like for the given user and object (e.g., Photographer, Videographer).
    """
    
    # Check if the user has already liked this object to avoid duplicate likes
    like_exists = PhotographerLike.objects.filter(
        user_id=user_id, 
        service_id=service_id
    ).exists()

    if not like_exists:
        # Create the like if it doesn't exist
        PhotographerLike.objects.create(
            vendor_id=vendor_id,
            user_id=user_id,
            service_id=service_id
        )
        return True
    else:
        # Delete the like if it exists
        PhotographerLike.objects.filter(
            user_id=user_id,
            service_id=service_id
        ).delete()
        return False 
    

@login_required
def toggle_save(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        service_id = request.POST.get('service_id')
        user_id = request.user.id
        # Call the like_object function to like the object
        saved = save_object(user_id, service_id, vendor_id)
        cache_key = f'photographer_service_details_{service_id}'
        cache.delete(cache_key)
    # Return JSON response with the new like state
    # data = {'saved': saved}
    # return JsonResponse(data, safe=False)
    return redirect(request.META.get('HTTP_REFERER', 'photographer:search_service'))

def save_object(user_id, service_id, vendor_id):
    """
    Add a save for the given user and object (e.g., Photographer, Videographer).
    """
    # Check if the user has already saved this object to avoid duplicate saves
    save_exists = PhotographerSave.objects.filter(
        user_id=user_id, 
        service_id=service_id
    ).exists()

    if not save_exists:
        # Create the save if it doesn't exist
        PhotographerSave.objects.create(
            vendor_id=vendor_id,
            user_id=user_id,
            service_id=service_id
        )
        return True
    else:
        # Delete the save if it exists
        PhotographerSave.objects.filter(
            user_id=user_id,
            service_id=service_id
        ).delete()
        return False
    
