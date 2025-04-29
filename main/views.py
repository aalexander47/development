from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib import messages

from vendor.models import Vendor, \
    Service as VendorServices

from photographer.models import \
    Service as PhotographerServices, \
    Gallery as PhotographerGallery

from invitation.models import Invitation as InvitationData, \
    Template as TemplateData

from .models import Contact
from .utils import get_client_ip, set_anonymous_user_cookie

from django.db.models import Count, Prefetch

from django.contrib.contenttypes.models import ContentType
import random, hashlib, re
from datetime import timedelta, datetime
# import messages

from vendor.views import get_cached_user


def eventic_homepage(request):
    return render(request, "main/pages/home.html")

# Create your views here.
def homepage_request(request):
    user = get_cached_user(request)# Get all VendorGallery objects

    vendors = Vendor.objects.prefetch_related('user').only('name', 'profile_picture', 'city', 'user__username').exclude(active_services={}).filter(is_active=True, is_verified=True, is_suspended=False).all()
    featured_vendors = random.sample(list(vendors), min(4, len(vendors)))

    # Photographers
    photographers = PhotographerServices.objects.prefetch_related('vendor').only('category', 'thumbnail', 'is_verified', 'vendor__name', 'vendor__city').filter(is_active=True, vendor__is_active=True, vendor__is_suspended=False).all()
    featured_photographers = random.sample(list(photographers), min(10, len(photographers)))

    for photographer in featured_photographers:
        # Replace spaces with hyphens
        slug = (photographer.vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        photographer.slug = slug


    # Fetch all vendor galleries with related vendor and content type
    vendor_galleries = PhotographerGallery.objects.select_related('vendor', 'service').only('vendor', 'service', 'image', 'album', 'description').filter(service__is_active=True, vendor__is_active=True, vendor__is_suspended=False).all()

    # Randomly select 10 vendor galleries
    random_galleries = random.sample(list(vendor_galleries), min(10, len(vendor_galleries)))

    # Prepare image data from preloaded content objects
    images = []
    for gallery in random_galleries:
        # content_obj = gallery.content_object
        if gallery:
            images.append({
                'url': gallery.image.url,
                'album': getattr(gallery, 'album', ''),
                'description': getattr(gallery, 'description', ''),
                'vendor': gallery.vendor
            })
            
    context = {
        'user': user,
        'portfolio_images': images,
        'featured_vendors': featured_vendors,
        'featured_photographers': featured_photographers
    }
    return render(request, "main/pages/home.html", context)

def create_vendor_service_for_existing_photographers():
    # Get the ContentType for Photographer model
    photographer_content_type = ContentType.objects.get_for_model(PhotographerServices)

    # Retrieve all Photographer instances
    photographers = PhotographerServices.objects.all()

    # Iterate through each photographer and create a corresponding Service object
    for photographer in photographers:
        # Check if a Service object already exists for this photographer to avoid duplicates
        if not VendorServices.objects.filter(content_type=photographer_content_type, object_id=photographer.id).exists():
            # Create a new Service entry for the photographer
            VendorServices.objects.create(
                vendor=photographer.vendor,  # Link to the vendor associated with the photographer
                content_type=photographer_content_type,  # Set the ContentType to Photographer
                object_id=photographer.id,  # Set the object_id to the Photographer's primary key
                content_object=photographer
            )

@set_anonymous_user_cookie
def contact_request(request):
    if request.method == "POST" and 'contact' in request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        # Get the IP address of the user
        cookie_uid = request.COOKIES.get('uid') if request.COOKIES.get('uid', None) else  hashlib.md5(f"{get_client_ip(request)}".encode()).hexdigest()

        Contact.objects.create(name=name, email=email, message=message, uid=cookie_uid)
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
        return redirect('main:contact')
    
    cookie_uid = request.COOKIES.get('uid') if request.COOKIES.get('uid', None) else  hashlib.md5(f"{get_client_ip(request)}".encode()).hexdigest()
    enquired = False
    if Contact.objects.filter(uid=cookie_uid).exists():
        enquired = True
    
    data = {
        'enquired': enquired
    }
    return render(request, "main/pages/contact.html", data)

def about_us_request(request):
    return render(request, "main/pages/about.html")

def terms_of_use_request(request):
    return render(request, "main/pages/terms-of-use.html")

def privacy_policy_request(request):
    return render(request, "main/pages/privacy-policy.html")

def payment_policy_request(request):
    return render(request, "main/pages/payment-policy.html")

def refund_policy_request(request):
    return render(request, "main/pages/refund-policy.html")

################## EVENTRON #####################

def vendor_request(request, username):
    try:
        vendor = Vendor.objects.prefetch_related(
            Prefetch('services'),
            Prefetch('legal'),
            Prefetch('gallery')
        ).annotate(
            services_count=Count('services'),
        ).get(user__username=username)
    except Vendor.DoesNotExist:
        messages.error(request, 'The vendor you are trying to access does not exist.')
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

    if vendor.services_count == 0:
        messages.error(request, 'The vendor you are trying to access has no services.')
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

    if not vendor.is_active:
        # Send message user the user that he is trying to access an inactive vendor
        messages.error(request, 'The vendor you are trying to access is inactive. Please contact the admin.')
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))
    
    if vendor.is_suspended:
        # Send message user the user that he is trying to access an inactive vendor
        messages.error(request, 'The vendor you are trying to access is suspended. Please contact the admin.')
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

    services = []
    for service in vendor.services.all():
        slug = (vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        service.content_object.slug = slug
        services.append(service)

    images = []
    if vendor.gallery.exists():
        for image in vendor.gallery.all():
            image = image.content_object
            images.append(image)

    if images:
        random.shuffle(images)
    
    images_1 = []
    images_2 = []
    images_3 = []

    portfolio_images = images[:12] if images else []
    # hero_images = images[8:13] if images else [] 

    # images = images[:4]

    carosal_images_count = 2 
    if len(images) > 4 and len(images) <= 6:
        carosal_images_count = 2
    elif len(images) >= 6 and len(images) <= 9:
        carosal_images_count = 3
    elif len(images) > 9:
        carosal_images_count = 4


    for image in images:
        if len(images_1) < carosal_images_count:
            images_1.append(image)
        elif len(images_2) < carosal_images_count:
            images_2.append(image)
        elif len(images_3) < carosal_images_count:
            images_3.append(image)

    data = {
        'vendor': vendor,
        'portfolio_images': portfolio_images,
        'hero_images': portfolio_images,
        'services': services,
        'images_1': images_1,
        'images_2': images_2,
        'images_3': images_3
    }
    return render(request, 'main/pages/eventron.html', data)

def vendor_profile_request(request, account_id, slug):
    vendor = Vendor.objects.prefetch_related(
        # Can fetch only required fields from services model. [thumbnail, category]
        Prefetch('services'),
        Prefetch('legal'),
        Prefetch('gallery')
    ).get(account_id=account_id)

    services = []
    for service in vendor.services.all():
        slug = (vendor.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        service.content_object.slug = slug
        services.append(service)

    images = []
    if vendor.gallery.exists():
        for image in vendor.gallery.all():
            image = image.content_object
            images.append(image)

    if images:
        random.shuffle(images)
        
    portfolio_images = images[:8] if images else []
    # hero_images = images[8:13] if images else []

    data = {
        'vendor': vendor,
        'portfolio_images': portfolio_images,
        'hero_images': portfolio_images,
        'services': services
    }
    return render(request, 'main/pages/vendor-profile.html', data)


def invitation_detail(request, id):
    invitation = InvitationData.objects.prefetch_related('template').filter(id=id).first()

    # Check if invitation exists
    if not invitation:
        messages.error(request, 'The invitation you are trying to access does not exist. Or expired.')
        return redirect('invitation:home')

    # Check if the invitation is expired
    if invitation.is_expired:
        # Check if the invitation is passed 15 days of expiration
        if (datetime.now() - invitation.end_date).days > 15:
            # Delete the invitation
            invitation.delete()

        data = {
            'message': 'This invitation has expired.'
        }
        return render(request, 'invitation/pages/expired_invitation.html', data)

    template_path = invitation.template.path
    
    data = {
        'invitation': invitation
    }
    return render(request, f'invitation/{ template_path }/details.html', data)
