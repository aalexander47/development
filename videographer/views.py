from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
import hashlib, re

from vendor.models import \
    Vendor, \
    Service as VendorService, \
    Lead as VendorLead, \
    Gallery as VendorGallery, \
    TeamMember

from user.models import \
    Lead as UserLead

from .models import \
    Service as VideographerService, \
    Review as VideographerReview, \
    ReportService as ReportVideographerService, \
    ReportReview as ReportVideographerReview, \
    Gallery as VideographerGallery, \
    Lead as VideographerLead, \
    Like as VideographerLike, \
    Save as VideographerSave, \
    CallbackRequest as VideographerCallbackRequest

from django.db.models import Q, Count, F, Value, CharField, Prefetch, Exists, OuterRef, Subquery
from django.db.models.functions import Concat
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from authenticator.decorators import has_permission
from uuid import uuid4
from django.conf import settings
from django.contrib import messages
from datetime import date, datetime, timedelta
from .tasks import send_callback_lead_email
from dashboard.data import services as videographer_services
from vendor.tasks import create_notification
from vendor.views import get_cached_user
from main.utils import get_client_ip, set_anonymous_user_cookie

#/////////////////   CMS   ////////////////
@has_permission('vendor')
def cms_dashboard(request):
    user = get_cached_user(request, 'vendor')
    context = {
        'cp': 'services',
        'user': user
    }
    return render(request, 'videographer/cms/pages/dashboard.html', context)

@has_permission('vendor')
def cms_reviews(request):
    user = get_cached_user(request, 'vendor')
    services = VideographerService.objects.only('id', 'vendor', 'category').prefetch_related(
            Prefetch('reviews', queryset=VideographerReview.objects.order_by('-created_at'))
        ).filter(user=user)
    
    reviews = []
    for service in services:
        slug = (service.vendor.name).lower().replace(" ", "-")
        slug = re.sub(r'[^\w-]', '', slug)
        for review in service.reviews.all():
            review.service.id = service.id
            review.service.slug = slug
            review.service.category = service.category
            reviews.append(review)
            
    context = {
        'cp': 'services',
        'reviews': reviews,
        'user': user
    }
    return render(request, 'videographer/cms/pages/reviews.html', context)

@has_permission('vendor')
def cms_settings(request):
    user = get_cached_user(request, 'vendor')
    context = {
        'cp': 'services',
        'user': user
    }
    return render(request, 'videographer/cms/pages/settings.html', context)

@has_permission('vendor')
def cms_create(request):
    user = get_cached_user(request, 'vendor')
    if request.method == 'POST' and 'create_service' in request.POST:
        vendor_id = request.POST.get('vendor_id', '')
        vendor_name = request.POST.get('vendor_name', '')
        if vendor_name:
            vendor_name = vendor_name.lower().replace(" ", "-")
        category = request.POST.get('category', '')
        price = request.POST.get('photoCost', "")
        price_unit = request.POST.get('photoCostPer', '')
        description = request.POST.get('description', '')
        thumbnail = request.FILES.get('thumbnail', None)
        startedIn = request.POST.get('startedIn', '')
        contact = request.POST.get('pointOfContact', 0)

        formatted_date = ""
        if startedIn:
            # Parse the date string as YYYY-MM
            date_obj = datetime.strptime(startedIn, "%Y-%m")
            # Create a new date object with the first day of the month
            formatted_date = date_obj.strftime("%Y-%m-%d")
        
        if not formatted_date:
            today = date.today()
            formatted_date = today.strftime("%Y-%m-%d")

        policy = {
            "userCancelPolicy": request.POST.get('userCancelPolicy', ''),
            'vendorCancelPolicy': request.POST.get('vendorCancelPolicy', ''),
            'paymentTerms': request.POST.get('paymentTerms', ''),   
            'termsAndConditions': request.POST.get('termsAndConditions', ''),
        }

        other = {
            "basicInfo": {},
            "otherCharges": {},
            "additionalInfo": {}
        }
        
        if category.lower() == "wedding":
            # Basic Info
            other['basicInfo']['offerEngagement'] = request.POST.get('offerEngagement', '') # Wedding
            # Other Charges
            other['otherCharges']['photoVideoCost'] = request.POST.get('photoVideoCost', "") # Wedding
            other['otherCharges']['photoVideoCostPer'] = request.POST.get('photoVideoCostPer', '') # Weddings

        other['basicInfo']['photographyStyle'] = request.POST.get('photographyStyle', '')
        other['otherCharges']['mostBookedPackage'] = request.POST.get('mostBookedPackage', '')
        other['otherCharges']['packageServiceDays'] = request.POST.get('packageServiceDays', '')
        # Additional Info
        other['additionalInfo']['citiesCovered'] = request.POST.get('citiesCovered', '')
        
        # Packages
        packages = []
        for i in range(len(request.POST.getlist('packageName'))):  # Iterate over each title
            package_name = request.POST.getlist('packageName')[i]
            if package_name:
                package_data = {
                    'name': package_name,
                    'price': request.POST.getlist('packagePrice')[i],
                    'pricePer': request.POST.getlist('packagePricePer')[i],
                    'details': request.POST.getlist('packageDetails')[i],
                }
                packages.append(package_data)

        other['packages'] = packages
        
        # Add-ons
        addOns = []
        for i in range(len(request.POST.getlist('addOnName'))):  # Iterate over each title
            addOn_name = request.POST.getlist('addOnName')[i]
            if addOn_name:
                addOn_data = {
                    'name': addOn_name,
                    'price': request.POST.getlist('addOnPrice')[i],
                    'pricePer': request.POST.getlist('addOnPricePer')[i],
                    'details': request.POST.getlist('addOnDetails')[i],
                }
                addOns.append(addOn_data) 

        other['addOns'] = addOns

        if thumbnail and thumbnail is not None:
            thumbnail.name = 'eventic' + '-' + vendor_name + '-' + str(category) + '-photography-' + str(uuid4())[:4] + '.' + thumbnail.name.split('.')[-1]

        service_detail = VideographerService.objects.create(
            vendor_id=vendor_id, 
            user=user, 
            category=category, 
            price=price,
            price_unit=price_unit, 
            description=description, 
            contact=contact,
            thumbnail=thumbnail,
            policy=policy,
            other=other,
            experience=formatted_date
        )

        slug = (vendor_name).lower().replace(" ", "-")
        slug = re.sub(r'[^\w-]', '', slug)
        service_detail.slug = slug
        content_type = ContentType.objects.get_for_model(VideographerService)
        VendorService.objects.create(vendor_id=vendor_id, content_type=content_type, object_id=service_detail.id)

        cache_keys_to_delete = [f'vendor_services_{user.id}', f'services_list_{user.id}', f'services_app_list_{user.id}']
        for key in cache_keys_to_delete:
            cache.delete(key)

        messages.success(request, "Service has been created successfully.")
        return redirect('vendor:Services')
    
    
    category = request.GET.get('category', '')
    category_form_template = ""
    if category:
        # Get the rendered form component
        team_members = TeamMember.objects.filter(vendor_id=user.vendor_id)
        rendered_form_component = render(request, f"videographer/cms/category_forms/_{category}.html", {'cp': 'create', 'teamMembers': team_members}).content.decode('utf-8')
        category_form_template = rendered_form_component
    
    category = request.GET.get('category', '')
    category_form_template = ""
    if category:
        # Get the rendered form component
        team_members = TeamMember.objects.filter(vendor_id=user.vendor_id)
        template_name = videographer_services['videographer'].get(category)['template']
        rendered_form_component = render(request, f"videographer/cms/category_forms/{template_name}.html", {'cp': 'create', 'teamMembers': team_members}).content.decode('utf-8')
        category_form_template = rendered_form_component

    vendor = Vendor.objects.get(user=user)

    context = {
        'cp': 'services',
        'page': 'create',
        'vendor': vendor,
        'user': user,
        'rendered_form': category_form_template,
        'category': category,
        'videographer_service_categories': videographer_services['videographer']
    }
    return render(request, 'videographer/cms/pages/create-or-update.html', context)

@has_permission('vendor')
def cms_update(request, id):
    user = get_cached_user(request, 'vendor')
    if request.method == 'POST' and 'update_service' in request.POST:
        service = get_object_or_404(VideographerService, id=id)
        service.price = request.POST.get('videoCost', "")
        service.price_unit = request.POST.get('videoCostUnit', '')
        service.description = request.POST.get('description', '')
        startedIn = request.POST.get('startedIn', '')
        service.is_active = request.POST.get('is_active', '') == 'on'
        service.contact = request.POST.get('pointOfContact', 0)

        formatted_date = ""
        if startedIn:
            # Parse the date string as YYYY-MM
            date_obj = datetime.strptime(startedIn, "%Y-%m")
            # Create a new date object with the first day of the month
            formatted_date = date_obj.strftime("%Y-%m-%d")
        
        if not formatted_date:
            today = date.today()
            formatted_date = today.strftime("%Y-%m-%d")

        service.experience = formatted_date

        service.policy = {
            "userCancelPolicy": request.POST.get('userCancelPolicy', ''),
            'vendorCancelPolicy': request.POST.get('vendorCancelPolicy', ''),
            'paymentTerms': request.POST.get('paymentTerms', ''),   
            'termsAndConditions': request.POST.get('termsAndConditions', ''),
        }

        other = {
            "basicInfo": {},
            "otherCharges": {},
            "additionalInfo": {}
        }

        if (service.category).lower() == "wedding":
            # Basic Info
            other['basicInfo']['offerEngagement'] = request.POST.get('offerEngagement', '') # Wedding

        other['basicInfo']['videographyStyle'] = request.POST.get('videographyStyle', '')
        other['otherCharges']['mostBookedPackage'] = request.POST.get('mostBookedPackage', '')
        other['otherCharges']['packageServiceDays'] = request.POST.get('packageServiceDays', '')
        # Additional Info
        other['additionalInfo']['citiesCovered'] = request.POST.get('citiesCovered', '')
        
        # Packages
        packages = []
        for i in range(len(request.POST.getlist('packageName'))):  # Iterate over each title
            package_name = request.POST.getlist('packageName')[i]
            if package_name:
                package_data = {
                    'name': package_name,
                    'price': request.POST.getlist('packagePrice')[i],
                    'pricePer': request.POST.getlist('packagePricePer')[i],
                    'details': request.POST.getlist('packageDetails')[i],
                }
                packages.append(package_data)

        other['packages'] = packages
        
        # Add-ons
        addOns = []
        for i in range(len(request.POST.getlist('addOnName'))):  # Iterate over each title
            addOn_name = request.POST.getlist('addOnName')[i]
            if addOn_name:
                addOn_data = {
                    'name': addOn_name,
                    'price': request.POST.getlist('addOnPrice')[i],
                    'pricePer': request.POST.getlist('addOnPricePer')[i],
                    'details': request.POST.getlist('addOnDetails')[i],
                }
                addOns.append(addOn_data)

        other['addOns'] = addOns

        service.other = other

        # Update Thumbnail
        thumbnail = request.FILES.get('thumbnail', None)
        file_exists = request.POST.get('file_exists')
        
        if file_exists == "removed":
            if service.thumbnail and default_storage.exists(service.thumbnail.name):
                default_storage.delete(service.thumbnail.name)
            service.thumbnail = ""

        if file_exists == "changed" and thumbnail:
            if service.thumbnail and default_storage.exists(service.thumbnail.name):
                default_storage.delete(service.thumbnail.name)

            thumbnail.name = 'eventic' + '-' + service.vendor.name.replace(' ', '-') + '-' + str(service.category) + '-vidoegraphy-' + str(uuid4())[:4] + '.' + thumbnail.name.split('.')[-1]
            service.thumbnail = thumbnail

        service.save()

        cache_keys_to_delete = [f'vendor_services_{user.id}', f'services_list_{user.id}', f'services_app_list_{user.id}']
        for key in cache_keys_to_delete:
            cache.delete(key)

        messages.success(request, "Service has been updated successfully.")
        return redirect('vendor:Services')

    service = get_object_or_404(VideographerService, id=id)
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

    rendered_form_component = render(request, f"videographer/cms/category_forms/_{service.category}.html", {'service': service, 'teamMembers': team_members}).content.decode('utf-8')
    context = {
        'cp': 'services',
        'page': 'update',
        'service': service,
        'vendor': vendor,
        'rendered_form': rendered_form_component,
        'user': user
    }
    return render(request, 'videographer/cms/pages/create-or-update.html', context)

@has_permission('vendor')
def cms_load_category_form_component(request):
    user = get_cached_user(request, 'vendor')
    category = request.GET.get('category', '')
    rendered_form_component = ""
    if category:
        team_members = TeamMember.objects.filter(vendor_id=user.vendor_id)
        rendered_form_component = render(request, f"videographer/cms/category_forms/_{category}.html", {'cp': 'create', 'teamMembers': team_members}).content.decode('utf-8')

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
        content_type = ContentType.objects.get_for_model(VideographerGallery)

        # Prepare lists for bulk creation
        videographer_gallery_instances = []
        vendor_gallery_instances = []

        # Loop through images and prepare instances
        for i, image in enumerate(image_files):
            if image:
                description = image_descriptions[i] if i < len(image_descriptions) else ''
                image.name = f"{image_name}-photography-{str(uuid4())[:4]}.{image.name.split('.')[-1]}"
                
                # Create VideographerGallery instance
                videographer_gallery = VideographerGallery(
                    service_id=service_id,
                    vendor_id=vendor_id,
                    image=image,
                    description=description
                )
                videographer_gallery_instances.append(videographer_gallery)

        # Bulk create VideographerGallery instances
        videographer_gallery_objects = VideographerGallery.objects.bulk_create(videographer_gallery_instances)

        # Prepare VendorGallery instances after VideographerGallery instances are saved
        for pg_instance in videographer_gallery_objects:
            vendor_gallery = VendorGallery(
                vendor_id=vendor_id,
                content_type=content_type,
                object_id=pg_instance.id
            )
            vendor_gallery_instances.append(vendor_gallery)

        # Bulk create VendorGallery instances
        VendorGallery.objects.bulk_create(vendor_gallery_instances)
        messages.success(request, "Images have been added successfully.")

        return redirect('videographer:Gallery')

    services = VideographerService.objects.only('id', 'vendor', 'category').prefetch_related(Prefetch('gallery')).filter(user=request.user)
    gallery = []

    vendor = None
    for service in services:
        slug = (vendor.name).lower().replace(" ", "-")
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
    return render(request, 'videographer/cms/pages/gallery.html', context)

@has_permission('vendor')
def cms_gallery_delete(request, id):
    # delete image
    image = get_object_or_404(VideographerGallery, id=id)
    if request.user != image.vendor.user:
        messages.error(request, "You don't have permission to delete this image.")
        return redirect('videographer:Gallery')
    image.delete()
    messages.success(request, "Image has been deleted successfully.")

    return redirect('videographer:Gallery')

@has_permission('vendor')
def cms_delete_service(request, id):
    if request.method == 'POST' and 'deleteServiceBtn' in request.POST:
        if id:
            service = get_object_or_404(VideographerService, id=id)
            service.delete()
            messages.success(request, "Service has been deleted successfully.")
        else:
            messages.error(request, "Service not found.")

    return redirect('vendor:Services')

#/////////////   Users   //////////////
def home(request):
    return render(request, 'videographer/home.html')

@set_anonymous_user_cookie
def request_callback(request, service_id, slug, vendor_id):
    if request.method == 'POST' and 'request_callback' in request.POST:
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        cookie_uid = request.COOKIES.get('uid') if request.COOKIES.get('uid', None) else  hashlib.md5(f"{get_client_ip(request)}".encode()).hexdigest()

        service = VideographerService.objects.prefetch_related('vendor', 'user').only('id', 'category', 'contact', 'user__id', 'user__username', 'user__first_name', 'user__last_name', 'vendor__id', 'vendor__email', 'vendor__name').get(pk=service_id)

        email_to = service.vendor.email
        poc = None
        if service.contact:
            poc = TeamMember.objects.get(pk=service.contact)
            email_to = poc.email

        # create callback request
        VideographerCallbackRequest.objects.create(vendor_id=vendor_id, name=name, email=email, phone=phone, message=message, service_id=service_id, uid=cookie_uid)
        VideographerLead.objects.create(vendor_id=vendor_id, service_id=service_id, uid=cookie_uid, lead_type='callback_request')

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
            description=f"Callback Request from {name.title()} for {(service.category).title()} Videographer Service.", 
            other={
                "service_id": service_id,
                "url": f"/videographer/service/{service_id}/{slug}",
                "client_name": name,
                "client_phone": phone,
                "client_email": email,
                "client_message": message
            }
        )
        messages.success(request, "Your request has been submitted successfully.")  

    return redirect('videographer:service', slug=slug)


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
        
        VideographerReview.objects.create(rating=rating, review=review, vendor_id=vendor_id, recommend_for=recommend_for, uid=uid, user=request.user, service_id=service_id, approved=approved)

        # Clear cache for service details page
        cache_key = f'videographer_service_details_{service_id}'
        cache.delete(cache_key)
        messages.success(request, "Your review has been submitted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))

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
        ReportVideographerService.objects.create(service_id=service_id, uid=uid, screenshot=screenshot, reason=reason, description=description, user=request.user)
        messages.success(request, "Your report has been submitted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))

@login_required(login_url='auth:login')
def report_review(request):
    if request.method == 'POST' and 'report_review' in request.POST:
        review_id = request.POST.get('review_id', "")
        reason = request.POST.get('report_reason', "")
        uid = str(uuid4())[:8]
        ReportVideographerReview.objects.create(review_id=review_id, uid=uid, reason=reason, user=request.user)
        messages.success(request, "Your report has been submitted successfully.")
    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))

@login_required(login_url='auth:login')
def delete_review(request):
    if request.method == 'POST' and 'delete_review' in request.POST:
        review_id = request.POST.get('review_id')
        review = get_object_or_404(VideographerReview, id=review_id, user=request.user)
        id = review.service_id
        review.delete()
        cache_key = f'videographer_service_details_{id}'
        cache.delete(cache_key)
        messages.success(request, "Your review has been deleted successfully.")

    # Redirect back to the referring page or a fallback URL
    return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))


# ////////////////    SEARCH    ///////////////////////
def search_by_service(request):
    return search(request, category=None)

def search(request, category):
    user = get_cached_user(request)
    query = request.GET.get('q', '')

    results = search_with_ranking(query, category)
    for result in results:
        result.category = result.category.replace("_", " ")

    vendor_service = f'{category.replace("_", " ")} ' if category and category is not None else ""

    data = {
        'query': query,
        'results': results,
        'eventron_service':  f'{vendor_service} Videographer',
        'user': user
    }
    return render(request, "videographer/pages/search.html", data)

def search_with_ranking(search_string, category):
    """
    Searches for individual words in a search string, ranks results, and filters based on a match threshold.

    Args:
        search_string: The string containing words to search for.

    Returns:
        A list of dictionaries containing matched models and their word match counts.
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
        "videographer", "videographers", "photography", "photo", "photos", 
    ]
    
    special_characters = ["#", "$", "%", "&","?", ".", ",", "!", ":", ";", '"', "'", "`", "-", "=", "+", "*", "/","|", "^", "(", ")", "[", "]", "{", "}"]

    categories = [
        "wedding",
        "birthday",
        "corporate",
        "event",
        "fashion",
        "drone",
        "landscape",
        "portrait"
    ]

    search_ingnored = stopwords + special_characters

    words = search_string.lower().split()  # Split search string into lowercase words

    if category is None:
        # Check if any word from the search string is in the categories list
        matching_category = next((word for word in words if word in categories), None)
        
        if matching_category:
            category = matching_category  # Set the category to the matching word

    conditions = Q(vendor__is_active=True) & Q(is_active=True)
    if category and category is not None:
        conditions &= Q(category__icontains=category)

    for word in words:
        if word not in search_ingnored:
            conditions &= Q(other__icontains=word) \
                                    | Q(vendor__name__icontains=word) \
                                    | Q(vendor__address__icontains=word) \
                                    | Q(vendor__city__icontains=word) \
                                    | Q(vendor__state__icontains=word) \
                                    | Q(vendor__pincode__icontains=word) 

    # Filter Service objects based on conditions
    cache_key_string = f'{search_string.replace(" ", "-")}{"_" + category.replace(" ", "-") + "_" if category and category is not None else "_videographers"}'
    cache_key = f'filtered_results_{cache_key_string}'
    results = cache.get(cache_key)

    if results is None:
        results = (
            VideographerService.objects
            .select_related('vendor')  # Fetching vendor in the same query
            .only('thumbnail', 'category', 'vendor__name', 'vendor__address', 'vendor__city', 'vendor__state', 'vendor__pincode', 'vendor', 'other', 'experience', 'price', 'price_unit', 'is_verified', 'ad_active', 'sponsorship_active')
            .filter(conditions)
            .annotate(
                slug=Concat(
                    F('vendor__name'),
                    Value('-'),
                    F('id'),
                    output_field=CharField()
                )
            )
        )
        for result in results:
            if result.thumbnail and default_storage.exists(result.thumbnail.name):
                result.has_thumbnail = True
            
            slug = (result.vendor.name).lower().replace(" ", "-")
            slug = re.sub(r'[^\w-]', '', slug)
            result.slug = slug

        cache.set(cache_key, results, timeout=60)  # Cache for 10 minute

    return results


@set_anonymous_user_cookie
def service_details(request, service_id, slug):
    user = get_cached_user(request)
    cookie_uid = hashlib.md5(f"user-{user.id}".encode()).hexdigest() if user.is_authenticated else request.COOKIES.get('uid')

    if request.method == 'POST' and 'lead' in request.POST:
        lead_type = request.POST.get('lead_type', '')
        service = VideographerService.objects.only('id', "vendor__id", 'contact').get(id=service_id)
        # create lead
        VideographerLead.objects.create(
            service_id=service_id,
            vendor_id=service.vendor.id,
            lead_type = lead_type,
            uid = cookie_uid
        )

        poc = None
        if service.contact:
            poc = TeamMember.objects.get(pk=service.contact)

        action = ''
        if lead_type == 'phone' or lead_type == 'call_slider':
            action = f"tel:+91{service.vendor.phone}" if poc is None else f'tel:+91{poc.phone}'
        elif lead_type == 'email':
            action = f"mailto:{service.vendor.email}" if poc is None else f'mailto:{poc.email}'
        elif lead_type == 'whatsapp':
            action = f"https://wa.me/91{service.vendor.phone}" if poc is None else f'https://wa.me/91{poc.whatsapp}'

        data = {
            'action': action
        }
        return JsonResponse(data, status=200, safe=False)

    # Define a unique cache key based on service ID
    # cache_key = f'videographer_service_details_{id}'
    # service_details = cache.get(cache_key)
    service_details = False

    if not service_details:
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

            service_details = VideographerService.objects.select_related('vendor').prefetch_related(
                Prefetch('gallery'),
                Prefetch('reviews', queryset=VideographerReview.objects.filter(reviews_conditions).order_by('-created_at')),
            ).annotate(
                total_leads=Count('leads', filter=Q(leads__created_at__gte=today - timedelta(days=30)), distinct=True),
                like_count=Count('likes', distinct=True),
                has_user_lead=Exists(
                    VideographerLead.objects.filter(
                        created_at__date=today,
                        lead_type='callback_request',
                        uid=cookie_uid,
                        service_id=OuterRef('pk')
                    )
                ),
                has_gallery=Exists(
                    VideographerService.objects.filter(
                        gallery__image__isnull=False,
                        gallery__image__gt='',  # Check if image field is not empty
                        id=OuterRef('pk')
                    )
                ),
                reviews_count=Count('reviews', 
                                    filter=Q(reviews__approved=True) | Q(reviews__user=user) if user.is_authenticated else Q(reviews__approved=True), 
                                    distinct=True),
                has_rated = Exists(
                    VideographerReview.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False),
                is_liked=Exists(
                    VideographerLike.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False),
                is_saved=Exists(
                    VideographerSave.objects.filter(service_id=OuterRef('pk'), user=user)
                ) if user.is_authenticated else Value(False)
            ).only(
                'id', 'category', 'description', 'price', 'price_unit', 'other', 'thumbnail', 'experience', 'vendor',
                'vendor__id', 'vendor__name', 'vendor__email', 'vendor__phone', 'vendor__whatsapp', 'vendor__bio',
                'vendor__address', 'vendor__city', 'vendor__state', 'vendor__country', 'vendor__pincode', 
                'vendor__website', 'vendor__facebook', 'vendor__instagram', 'vendor__twitter',
                'leads', 'leads__id', 'leads__uid', 'leads__lead_type', 'leads__created_at',
                'gallery', 'gallery__image',
            ).filter(conditions).get(id=service_id)

        except VideographerService.DoesNotExist:
            messages.error(request, "(｡•́︿•̀｡) Service does not exist.")
            return redirect('videographer:search_service')
        
        service_details.todays_user_leads = todays_user_leads

        # Additional flags based on the 'other' JSONField
        other_data = service_details.other or {}
        service_details.has_packages = True if other_data.get('packages', {}) else False
        service_details.has_addOns = True if other_data.get('addOns', {}) else False
        service_details.has_faqs = True if other_data.get('faqs', {}) else False

        # Check if the service thumbnail exists
        service_details.has_thumbnail = bool(service_details.thumbnail and default_storage.exists(service_details.thumbnail.name))

        # Get the content type for the service
        service_details.content_type = ContentType.objects.get_for_model(service_details)
        service_details.slug = slug

        # Store the service details in cache

        for image in service_details.gallery.all():
            if image.image and default_storage.exists(image.image.name):
                image.has_image = True
            else:
                image.has_image = False

        # CACHE_TIMEOUT = 60 * 15  # 15 minutes
        # cache.set(cache_key, service_details, CACHE_TIMEOUT)

    # Prepare the context and render the response
    context = {
        'service': service_details,
        'user': user
    }
    return render(request, 'videographer/pages/details.html', context)

@login_required
def toggle_like(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        service_id = request.POST.get('service_id')
        user_id = request.user.id

        # Call the like_object function to like the object
        liked = like_object(user_id, service_id, vendor_id)
        
        cache_key = f'videographer_service_details_{service_id}'
        cache.delete(cache_key)

    # Return JSON response with the new like state
    data = {'liked': liked}
    return JsonResponse(data, status=200, safe=False)
    # return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))

def like_object(user_id, service_id, vendor_id):
    """
    Add a like for the given user and object (e.g., Photographer, Videographer).
    """
    
    # Check if the user has already liked this object to avoid duplicate likes
    like_exists = VideographerLike.objects.filter(
        user_id=user_id, 
        service_id=service_id
    ).exists()

    if not like_exists:
        # Create the like if it doesn't exist
        VideographerLike.objects.create(
            vendor_id=vendor_id,
            user_id=user_id,
            service_id=service_id
        )
        return True
    else:
        # Delete the like if it exists
        VideographerLike.objects.filter(
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
        cache_key = f'videographer_service_details_{service_id}'
        cache.delete(cache_key)
    # Return JSON response with the new like state
    # data = {'saved': saved}
    # return JsonResponse(data, safe=False)
    return redirect(request.META.get('HTTP_REFERER', 'videographer:search_service'))

def save_object(user_id, service_id, vendor_id):
    """
    Add a save for the given user and object (e.g., Photographer, Videographer).
    """
    # Check if the user has already saved this object to avoid duplicate saves
    save_exists = VideographerSave.objects.filter(
        user_id=user_id, 
        service_id=service_id
    ).exists()

    if not save_exists:
        # Create the save if it doesn't exist
        VideographerSave.objects.create(
            vendor_id=vendor_id,
            user_id=user_id,
            service_id=service_id
        )
        return True
    else:
        # Delete the save if it exists
        VideographerSave.objects.filter(
            user_id=user_id,
            service_id=service_id
        ).delete()
        return False
    
