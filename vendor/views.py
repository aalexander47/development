from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group
from .models import Vendor, LegalDetail, ReportIssue, TeamMember, TrackBilling, AppliedReferral
from user.models import UserProfile, Notification
from payment.models import Transaction
from dashboard.models import Pricing, Coupon
from dashboard.data import services as platform_services

from payment.views import create_rezorpay_payment

from django.http import JsonResponse
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db.models import Count, Prefetch, Q, Exists, OuterRef
from authenticator.decorators import has_permission
from django.contrib import messages
from uuid import uuid4
from django.conf import settings
from user.utils import get_cached_user
from .utils import get_cached_vendor, account_id_to_referral_code
import time, io, base64, json, re
import matplotlib.pyplot as plt
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.utils.timezone import now
from collections import defaultdict
from dateutil.relativedelta import relativedelta


@has_permission('vendor')
def dashboard_cms_view(request):
    user = get_cached_user(request, 'vendor')

    vendor = Vendor.objects.filter(user=user).annotate(
        services_count=Count('services', distinct=True),
        team_count=Count('team', distinct=True),
        leads_count=Count('leads', distinct=True),
        likes_count=Count('likes', distinct=True),
        saves_count=Count('saves', distinct=True),
    ).only('name', 'credits', 'is_suspended', 'is_verified', 'is_active', 'bill').get()
    
    context = {
        'cp': 'dashboard',
        'vendor': vendor,
        'user': user,
    }
    return render(request, 'vendor/cms/pages/dashboard.html', context)

@login_required
def profile_cms_view(request):
    user = get_cached_user(request, 'vendor')
    context = {
        'cp': 'profile',
        'user': user
    }
    return render(request, 'user/cms/pages/profile.html', context)

@has_permission('vendor')
def details_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')
    
    vendor = Vendor.objects.get(user_id=user.id)

    if request.method == 'POST' and 'update_vendor_details' in request.POST:
        name = request.POST.get("name", "")
        vendor.name = name.strip()
        vendor.bio = request.POST.get("bio").strip()
        # Contact Details
        vendor.email = request.POST.get("email", '').strip()
        vendor.phone = request.POST.get("phone", "").strip()
        vendor.whatsapp = request.POST.get("whatsapp", "").strip()
        # Contact Time
        vendor.opening_time = request.POST.get("opening_time", None)
        vendor.closing_time = request.POST.get("closing_time", None)
        # Address Details
        vendor.address = request.POST.get("address", "").strip()
        vendor.city = request.POST.get("city", "").strip()
        vendor.state = request.POST.get("state", "")
        vendor.country = request.POST.get("country", "India")
        vendor.pincode = request.POST.get("pincode", "").strip()
        # Social Feeds
        vendor.instagram = request.POST.get("instagram", "").strip()
        vendor.facebook = request.POST.get("facebook", "").strip()
        vendor.twitter = request.POST.get("twitter", "").strip()
        vendor.website = request.POST.get("website", "").strip()
        vendor.embed_map = request.POST.get("embed_map", "").strip()
        vendor.is_active = True

        # update profile picture
        profile_picture = request.FILES.get('profile_picture', None)
        file_exists = request.POST.get('file_exists')
        
        if file_exists == "removed":
            if vendor.profile_picture and default_storage.exists(vendor.profile_picture.name):
                default_storage.delete(vendor.profile_picture.name)
            vendor.profile_picture = ""

        if file_exists == "changed" and profile_picture:
            if vendor.profile_picture and default_storage.exists(vendor.profile_picture.name):
                default_storage.delete(vendor.profile_picture.name)

            profile_picture.name = 'eventic' + '-' + (vendor.name).replace(' ', '_') + '-'+ str(uuid4())[:4] + '.' + profile_picture.name.split('.')[-1]
            vendor.profile_picture = profile_picture

        vendor.save()

        # cache_user_key = f'cached_user_{user.id}'
        # cache.delete(cache_user_key)
        cache_key = f'cached_vendor_{user.id}'
        cache.delete(cache_key)
        messages.success(request, 'Vendor Details Updated')
        return redirect("vendor:Details")
    
    if vendor.opening_time:
        vendor.opening_time = datetime.strptime(str(vendor.opening_time), "%H:%M:%S").strftime("%H:%M")

    if vendor.closing_time:
        vendor.closing_time = datetime.strptime(str(vendor.closing_time), "%H:%M:%S").strftime("%H:%M")

    context = {
        'cp': 'details',
        'vendor': vendor,
        'user': user
    }
    return render(request, 'vendor/cms/pages/details.html', context)

@has_permission('vendor')
def services_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')

    if not user.vendor_is_active:
        messages.error(request, 'Your account is not active. Please update your business details. To get access to all features')
        return redirect('vendor:Details')

    # Cache keys
    vendor_cache_key = f'vendor_services_{user.id}'
    services_cache_key = f'services_list_{user.id}'
    services_app_list_cache_key = f'services_app_list_{user.id}'

    # Fetch from cache
    vendor = cache.get(vendor_cache_key)
    services = cache.get(services_cache_key)
    services_app_list = cache.get(services_app_list_cache_key)

    if not vendor or not services:
        # Fetch Vendor and prefetch related services and service object fields
        vendor = Vendor.objects.prefetch_related('services', 'services__content_object').only('id', 'name').get(user=user)
        
        # Prefetch services related to the vendor
        services = (
            vendor.services.select_related('content_type')
            .prefetch_related('content_object__vendor', 'content_object__user')  # Prefetch nested relationships in service object
        )

        # Create slugs and add to services
        service_list = []
        # Listed services list
        services_app_list = set()

        for service in services:
            slug = (vendor.name).lower().replace(" ", "-")
            slug = re.sub(r'[^\w-]', '', slug)
            service.slug = slug
            service_list.append(service)
            services_app_list.add(service.content_type.app_label)

        # Cache the vendor and services
        # cache.set(vendor_cache_key, vendor, timeout=300)
        # cache.set(services_cache_key, service_list, timeout=300)
        # cache.set(services_app_list_cache_key, services_app_list, timeout=300)
    else:
        service_list = services
        services_app_list = set(service.content_type.app_label for service in service_list)
        
    # Prepare context
    context = {
        'cp': 'services',
        'vendor': vendor,
        'services': service_list,
        'services_app_list': services_app_list,
        'user': user
    }
    return render(request, 'vendor/cms/pages/services.html', context)

@has_permission('vendor')
def notifications_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')

    if request.method == 'POST' and 'mark_all_as_read' in request.POST:
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        return redirect('vendor:Notifications')
    
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as read.")
            return redirect('vendor:Notifications')
        notification.is_read = True
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as read.')
        return redirect('vendor:Notifications')

    if request.method == 'POST' and 'mark_as_unread' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as unread.")
            return redirect('vendor:Notifications')
        notification.is_read = False
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as unread.')
        return redirect('vendor:Notifications')
    
    if request.method == 'POST' and 'delete_notification' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if request.user != notification.user:
            messages.error(request, "You don't have permission to delete this notification.")
            return redirect('vendor:Notifications')
        notification.delete()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, "Notification has been deleted successfully.")
        return redirect('vendor:Notifications')

    # Cache keys for both all notifications and unread notifications
    cached_notification_key = f'cached_notifications_{user.id}'
    cached_unread_key = f'cached_unread_notifications_{user.id}'

    # Fetch unread notifications from cache
    unread_notifications = cache.get(cached_unread_key)
    
    # Only update unseen notifications if there are any in the cache
    if not unread_notifications:
        # Mark unseen notifications as seen and update them
        Notification.objects.filter(user=user, seen=False).update(seen=True)
        notification_count_key = f'notification_count_{user.id}'
        cache.delete(notification_count_key)
        
        # Cache empty unread notifications to avoid re-querying in this session
        cache.set(cached_unread_key, [], timeout=300)
    
    # Fetch the latest 25 notifications from cache
    notifications = cache.get(cached_notification_key)
    
    if not notifications:
        # Fetch only the latest 25 notifications in a single query with efficient ordering
        all_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:25]

        # Cache the notifications for future access
        cache.set(cached_notification_key, all_notifications, timeout=300)  # Cache for 5 minutes
    else:
        all_notifications = notifications

    context = {
        'cp': 'notifications',
        'notifications': all_notifications,  # All notifications for the user
        'user': user
    }
    return render(request, 'vendor/cms/pages/notifications.html', context)

@has_permission('vendor')
def billing_cms_view(request):
    user = get_cached_user(request, 'vendor')

    if request.method == 'POST' and 'payWithCredits' in request.POST:
        vendor = Vendor.objects.get(user=user)
        
        if vendor.bill > vendor.credit:
            deducted_amount = vendor.credit
            bill = vendor.bill - vendor.credit
            vendor.bill = bill
            vendor.credits = 0
        elif vendor.bill == vendor.credit:
            deducted_amount = vendor.credit
            vendor.bill = 0
            vendor.credits = 0
        elif vendor.bill < vendor.credit:
            deducted_amount = vendor.bill
            vendor.credits = vendor.credits - vendor.bill
            vendor.bill = 0

        vendor.save()

        Transaction.objects.create(user=user, transaction_type='debit', amount=deducted_amount, method='point', description='Bill settlement.')

        messages.success(request, 'Bill settled successfully')
        return redirect('vendor:Billing')
 
    vendor = Vendor.objects.annotate(
        services_count=Count('services', distinct=True),
        has_billed_today=Exists(TrackBilling.objects.filter(vendor=OuterRef('pk'), created_at__date=now().date())), # Check if track_billing exists for the today
    ).only('name', 'credits', 'active_services', 'active_features', 'is_suspended', 'is_verified', 'is_active', 'bill').get(user=user)

    estimated_bill = vendor.bill
    # Billing calculated today check if the billing is already done

    # Get the pricing 
    pricing_tags = Pricing.objects.all()
    pricing_dict = {price.tag.lower(): {'price': price.price, 'unit': price.unit} for price in pricing_tags}

    # Get the remaining days for the current month
    current_date = now()
    start_of_current_month = current_date.replace(day=1)
    remaining_days = (start_of_current_month + relativedelta(months=1) - current_date).days
    remaining_days = remaining_days - 1 if vendor.has_billed_today else remaining_days 

    # Get the total number of days in the current month
    total_days_in_current_month = (start_of_current_month + relativedelta(months=1) - start_of_current_month).days

    # Calculate the estimated bill based on active features and services
    estimated_bill_for_features = 0
    estimated_bill_for_services = 0
    estimated_bill_for_other_fee = 0
    active_features = []
    active_services = []

    for key, value in vendor.active_features.items():
        key = key.split("-")[0]
        if key in pricing_dict and value:
            estimated_bill += pricing_dict[key]['price'] * remaining_days
            estimated_bill_for_features += pricing_dict[key]['price'] * remaining_days

    for key, value in vendor.active_services.items():
        key = key.split("-")[0]
        if key in pricing_dict and value:
            estimated_bill += pricing_dict[key]['price'] * remaining_days
            estimated_bill_for_services += pricing_dict[key]['price'] * remaining_days
            _service = key.split("_")[0]
            _category = key.split("_")[1]
            _service_data = platform_services[_service][_category]
            _service_data['price'] = pricing_dict[key]['price']
            _service_data['unit'] = pricing_dict[key]['unit']
            active_services.append(_service_data)

    # Get the platform fees as well
    estimated_bill_for_other_fee += (pricing_dict['platform_fee']['price'] / total_days_in_current_month) * remaining_days
    estimated_bill += (pricing_dict['platform_fee']['price'] / total_days_in_current_month) * remaining_days
    # Round the estimated bill to 2 decimal places
    estimated_bill = round(estimated_bill, 2)
    estimated_bill_for_other_fee = round(estimated_bill_for_other_fee, 2)

    current_date = now()
    start_of_current_month = current_date.replace(day=1)
    six_months_ago = start_of_current_month - relativedelta(months=5)

    # Fetch data for the last 6 months
    billings = TrackBilling.objects.filter(vendor_id=vendor.id, created_at__gte=six_months_ago)

    # Initialize a dictionary for monthly totals
    monthly_data = defaultdict(lambda: {"other": 0, "active_features": 0, "active_services": 0})
    
    # Populate the dictionary with billing data
    for billing in billings:
        month_key = billing.created_at.strftime("%Y-%m")
        if month_key == current_date.strftime("%Y-%m") and billing.created_at > current_date:
            continue

        pricing = billing.pricing  # Assuming 'pricing' is stored as JSON
        monthly_data[month_key]["other"] += pricing["other"]
        monthly_data[month_key]["active_features"] += pricing["active_features"]
        monthly_data[month_key]["active_services"] += pricing["active_services"]

    # Generate the last 6 months' keys
    month_keys = [(start_of_current_month - relativedelta(months=i)).strftime("%Y-%m") for i in range(6)]

    # Ensure each month has a value (default 0 if missing)
    graph_data = {
        "months": sorted(month_keys, reverse=True),
        "other_totals": [round(monthly_data[month]["other"], 2) for month in month_keys],
        "active_features_totals": [round(monthly_data[month]["active_features"], 2) for month in month_keys],
        "active_services_totals": [round(monthly_data[month]["active_services"], 2) for month in month_keys],
    }

    if vendor.bill > 0:
        payment = create_rezorpay_payment(amount=vendor.bill, payment_type='vendor_bill_settlement_payment')
    else:
        payment = None
    
    vendor.referral_code = account_id_to_referral_code(vendor.account_id)

    context = {
        'cp': 'billing',
        'vendor': vendor,
        'user': user,
        'payment': payment,
        'graph_data' : json.dumps(graph_data),
        'estimated_bill': estimated_bill,
        'estimated_bill_for_features': estimated_bill_for_features,
        'estimated_bill_for_services': estimated_bill_for_services,
        'estimated_bill_for_other_fee': estimated_bill_for_other_fee,
        'active_features': active_features,
        'active_services': active_services
    }
    return render(request, 'vendor/cms/pages/billing.html', context)

@has_permission('vendor')
def approve_referral(request, vendor_id):
    user = get_cached_user(request, 'vendor')
    # Get both the vendor and the referred vendor
    vendor = Vendor.objects.get(user=user)
    referred_to = Vendor.objects.filter(id=vendor_id).first()
    referral = AppliedReferral.objects.filter(vendor=referred_to, referred_by=vendor).first()

    if not referred_to or not referral:
        messages.error(request, 'Invalid referral request.')
        return redirect(request.META.get('HTTP_REFERER', 'vendor:Nofications'))

    # Check if the referred_to is active and added a service to the platform
    if not referred_to.is_active:
        messages.error(request, 'The referred vendor is not active.')
        return redirect(request.META.get('HTTP_REFERER', 'vendor:Nofications'))
    
    if not referred_to.active_services:
        messages.error(request, 'The referred vendor has not added any services to the platform.')
        return redirect(request.META.get('HTTP_REFERER', 'vendor:Nofications'))
    
    # Update the referral status to approved
    referral.approved = True
    referral.save()

    credits_to_referrer = 100 # Credits to the referrer
    credits_to_referred = 50 # Credits to the referred vendor

    Transaction.objects.create(
        user=request.user,
        amount=credits_to_referred, 
        transaction_type='credit', 
        method='point', 
        description=f"Referral bonus for {referred_to.name}. {credits_to_referred} credit points added.", 
    )
    vendor.credits += credits_to_referred
    vendor.save()

    Transaction.objects.create(
        user=referred_to.user,
        amount=credits_to_referrer, 
        transaction_type='credit', 
        method='point', 
        description=f"Referral bonus for {vendor.name}. {credits_to_referrer} credit points added.", 
    )
    referred_to.credits += credits_to_referrer
    referred_to.save()

    messages.success(request, 'Referral request approved successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'vendor:Nofications'))

def duplicate_records_for_yesterday():
    # Step 1: Get today's records
    today = now().date()
    yesterday = today - timedelta(days=1)

    today_records = TrackBilling.objects.filter(created_at__date=today)

    # Step 2: Duplicate records for yesterday
    new_records = []
    for record in today_records:
        # Create a new instance with modified date
        new_record = TrackBilling(
            vendor=record.vendor,
            amount=record.amount,
            active_services=record.active_services,
            active_features=record.active_features,
            other=record.other,
            created_at=yesterday,  # Set to yesterday
            updated_at=yesterday,  # Optional: Set updated_at to yesterday as well
        )
        new_records.append(new_record)

    # Step 3: Bulk create the new records
    TrackBilling.objects.bulk_create(new_records)

    return print(f"Created {len(new_records)} records for yesterday.")

@has_permission('vendor')
def transactions_cms_view(request):
    user = get_cached_user(request, 'vendor')
    
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'cp': 'billing',
        'user': user,
        'transactions': transactions
    }
    return render(request, 'vendor/cms/pages/transactions.html', context)

@has_permission('vendor')
def credit_plans_cms_view(request):
    user = get_cached_user(request, 'vendor')

    plan_details = {
        'basic': {
            'price': 1000,
            'credits': 1000,
            'icon': 'flash-dynamic-color.png'
        },
        'standard': {
            'price': 2250,
            'credits': 2500,
            'icon': 'fire-dynamic-color.png'
        },
        'premium': {
            'price': 4500,
            'credits': 5000,
            'icon': 'medal-dynamic-color.png'
        }
    }
    
    if request.method == 'POST':
        credit_plan = request.POST.get('payment_type', "")
        
        if credit_plan == 'basic':
            amount = plan_details['basic']['price']
        elif credit_plan == 'standard':
            amount = plan_details['standard']['price']
        elif credit_plan == 'premium':
            amount = plan_details['premium']['price']
        else:
            amount = 0

        if amount == 0:
            messages.error(request, 'Invalid credit plan')
            return redirect('vendor:CreditPlans')
        try:
            payment = create_rezorpay_payment(amount=amount, payment_type=f'credit_buy_{credit_plan}_plan')
            # Return the order ID and success status
            return JsonResponse({"success": True, "payment": payment}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500, safe=False)
        
    payment = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    
    context = {
        'cp': 'billing',
        'user': user,
        'payment': payment,
        'plans': plan_details
    }
    return render(request, 'vendor/cms/pages/credit_plans.html', context)

@has_permission('vendor')
def settings_cms_view(request):
    user = get_cached_user(request, 'vendor')
    vendor = Vendor.objects.only('auto_bill_settlement_credits').filter(user=user).get()

    if request.method == 'POST' and 'update_vendor_settings' in request.POST:
        auto_bill_settlement_credits = request.POST.get("auto_bill_settlement_credits", "") == "on"
        vendor.auto_bill_settlement_credits = auto_bill_settlement_credits
        vendor.save()

        messages.success(request, 'Settings updated successfully')
        return redirect('vendor:Settings')

    if request.method == 'POST' and 'delete_account_btn' in request.POST:
        password = request.POST.get("password")
        confession = request.POST.get("confession", "") == "DELETE"
        if not confession:
            messages.error(request, 'Please confirm that you want to delete your account')
            return redirect('vendor:Details')

        # Check if the password is correct
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password')
            return redirect('vendor:Details')
        else:
            # Remove the vendor group from the user
            user.groups.remove(Group.objects.get(name='vendor'))

            # Remove the vendor from the database
            vendor.delete()
            
            cache_key = f"user_groups_{request.user.id}"
            cache.delete(cache_key)
            cache_key = f'cached_vendor_{user.id}'
            cache.delete(cache_key)

            messages.success(request, 'Account deleted successfully')
            return redirect('auth:auth_redirect_view')
    
    context = {
        'cp': 'settings',
        'user': user,
        'vendor': vendor
    }
    return render(request, 'vendor/cms/pages/settings.html', context)

@has_permission('vendor')
def team_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')
    
    if not user.vendor_is_active:
        messages.error(request, 'Your account is not active. Please update your business details. To get access to all features')
        return redirect('vendor:Details')
    
    if request.method == 'POST' and 'add_team_member' in request.POST:
        name = request.POST.get("name", "")
        role = request.POST.get("role", "")
        phone = request.POST.get("phone", "")
        whatsapp = request.POST.get("whatsapp", "")
        email = request.POST.get("email", "")

        TeamMember.objects.create(
            vendor=request.user.vendor,
            name=name,
            role=role,
            phone=phone,
            whatsapp=whatsapp,
            email=email
        )

        # Invalidate the cache
        cache_key = f'team_members_{user.id}'
        cache.delete(cache_key)
        messages.success(request, 'Team Member Added')
        return redirect(request.META.get('HTTP_REFERER', 'vendor:Team'))

    if request.method == 'POST' and 'update_team_member' in request.POST:
        id = request.POST.get("member_id", "")
        name = request.POST.get("name", "")
        role = request.POST.get("role", "")
        phone = request.POST.get("phone", "")
        whatsapp = request.POST.get("whatsapp", "")
        email = request.POST.get("email", "")

        TeamMember.objects.filter(id=id).update(
            name=name,
            role=role,
            phone=phone,
            whatsapp=whatsapp,
            email=email
        )

        # Invalidate the cache
        cache_key = f'team_members_{user.id}'
        cache.delete(cache_key)
        messages.success(request, 'Team Member Updated')
        return redirect("vendor:Team")

    if request.method == 'POST' and 'remove_team_member' in request.POST:
        id = request.POST.get("member_id", "")
        TeamMember.objects.get(id=id).delete()

        # Invalidate the cache
        cache_key = f'team_members_{user.id}'
        cache.delete(cache_key)
        messages.success(request, 'Team Member Removed')
        return redirect("vendor:Team")

    vendor = get_cached_vendor(request)
    # Define a cache key based on the vendor ID
    cache_key = f'team_members_{user.id}'

    # Try to get the cached team members
    team_members = cache.get(cache_key)

    # If not found in cache, query the database and cache the result
    if team_members is None:
        team_members = TeamMember.objects.filter(vendor=vendor).order_by('-created_at')
        cache.set(cache_key, team_members, timeout=600)  # Cache for 600 seconds (10 minutes)

    context = {
        'cp': 'details',
        'team_members': team_members,
        'user': user
    }
    return render(request, 'vendor/cms/pages/team.html', context)

@has_permission('vendor')
def eps_score_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')
    
    if not user.vendor_is_active:
        messages.error(request, 'Your account is not active. Please update your business details. To get access to all features')
        return redirect('vendor:Details')
    
    context = {
        'cp': 'epss',
        'user': user
    }
    return render(request, 'vendor/cms/pages/EPS_score.html', context)

@has_permission('vendor')
def legal_cms_view(request):
    user = get_cached_user(request, 'vendor')
    if user.vendor_is_suspended:
        return redirect('vendor:Dashboard')
    
    if not user.vendor_is_active:
        messages.error(request, 'Your account is not active. Please update your business details. To get access to all features')
        return redirect('vendor:Details')
    
    vendor = Vendor.objects.only('name').prefetch_related('legal').get(user=request.user)

    if request.method == 'POST' and 'update_legal_details' in request.POST:
        terms_conditions = request.POST.get("terms_conditions", "")
        cancellation_policy = request.POST.get("cancellation_policy", "")
        refund_policy = request.POST.get("refund_policy", "")
        payment_policy = request.POST.get("payment_policy", "")

        try:
            LegalDetail.objects.update_or_create(
                vendor=vendor,
                user=user,
                defaults={
                    'terms_conditions': terms_conditions,
                    'cancellation_policy': cancellation_policy,
                    'refund_policy': refund_policy,
                    'payment_policy': payment_policy
                }
            )
            messages.success(request, 'Legal details updated successfully')
        except IntegrityError as e:
            # Handle the integrity error if needed
            print(f"IntegrityError: {e}")
            messages.error(request, 'Failed to update legal details')
            
        return redirect('vendor:Legal') 

    context = {
        'cp': 'details',
        'vendor': vendor,
        'user': user
    }
    return render(request, 'vendor/cms/pages/legal.html', context)

@has_permission('vendor')
def get_component(request, component):
    instance = Vendor.objects.prefetch_related(
        Prefetch('services')
    ).get(user=request.user)  
    
    if instance:
        enrolled_services = []
        if instance.services:
            _services = instance.services.all()
            for _ in _services:
                _enrolled_service_name = _.type + '__' + _.category
                enrolled_services.append(_enrolled_service_name)
    context = {'enrolled_services': enrolled_services}
    return render(request, f'vendor/services/_{component}.html', context)

@has_permission('vendor')
def report_issue(request):
    if request.method == 'POST' and 'report_issue' in request.POST:
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        screenshot = request.FILES.get('screenshot', None)
        if screenshot and screenshot is not None:
            screenshot.name = f"screenshot-{str(uuid4())[:8]}.{screenshot.name.split('.')[-1]}"

        ReportIssue.objects.create(title=title, description=description, screenshot=screenshot, user=request.user)
        messages.success(request, "Your report has been submitted successfully.")

    return redirect('vendor:Details')