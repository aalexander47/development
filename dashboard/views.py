from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.timezone import now, make_aware
from django.utils.dateparse import parse_datetime
from django.core.files.storage import default_storage
from vendor.models import Vendor, Service
from user.models import UserProfile, Notification
from main.models import ErrorLog
from invitation.models import Invitation as InvitationModel, Template as TemplateModel
from .models import Pricing, Coupon
from django.db.models import Count, Prefetch, Q, Avg, Sum ,F # Import Q object for complex filtering
from django.db.models.functions import TruncDay
from authenticator.decorators import has_permission
from django.core.cache import cache
from django.contrib import messages
from user.utils import get_cached_user
from payment.views import calculate_price
from core.utils import send_email_with_backend
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from invitation.models import Review, ReportReview
from django.db.models import Case, When, IntegerField


# Create your views here.
@has_permission('admin, operations, developer')
def dashboard_cms_view(request):
    user = get_cached_user(request, 'staff')
    current_datetime = now().strftime("%Y-%m-%dT%H:%M")
    if request.method == 'POST' and 'calculate_price' in request.POST:
        if user.is_superuser or user.is_admin:
            created_at_input = request.POST.get('created_at', None)
            if created_at_input is not None:
                created_at_input = make_aware(parse_datetime(created_at_input))
                if created_at_input > now():
                    messages.error(request, 'Please select a date in the past.')
                    return redirect('dashboard:Dashboard')
            calculate_price(request, created_at_input)
        else:
            messages.error(request, 'You do not have permission to calculate pricing')
        return redirect('dashboard:Dashboard')
    
    # Aggregated counts in fewer queries
    vendors = Vendor.objects.only(
            'is_active', 'is_verified', 'is_suspended', 'active_services', 'bill', 'credits', 'id'
        ).all()
    users_count = User.objects.count()

    # Staff users, pending payment users, and active/inactive vendors counts
    staff_users_count = User.objects.filter(is_staff=True).count()
    pending_payment_users_count = User.objects.filter(groups__name='pending_payment').count()

    vendors_count = 0
    active_vendors_count = 0
    inactive_vendors_count = 0
    verified_vendors_count = 0
    suspended_vendors_count = 0

    # Active/inactive services counts
    services_count = 0
    active_services_count = 0
    inactive_services_count = 0
    vendors_with_services = 0

    total_bill = 0
    total_credits = 0

    for vendor in vendors:
        vendors_count += 1
        for value in vendor.active_services.values():
            services_count += 1
            if value:
                active_services_count += 1
            else:
                inactive_services_count += 1

        if vendor.is_active:
            active_vendors_count += 1
        else:
            inactive_vendors_count += 1

        if vendor.is_verified:
            verified_vendors_count += 1

        if vendor.is_suspended:
            suspended_vendors_count += 1

        if vendor.active_services.items():
            vendors_with_services += 1
        
        total_bill += vendor.bill
        total_credits += vendor.credits
        
    # Bugs count
    bugs_count = ErrorLog.objects.count()

    context = {
        'cp': 'dashboard',
        'user': user,
        "current_datetime": current_datetime,
        'vendors_count': vendors_count,
        'services_count': services_count,
        'users_count': users_count,
        'staff_users_count': staff_users_count,
        'pending_payment_users_count': pending_payment_users_count,
        'active_vendors_count': active_vendors_count,
        'inactive_vendors_count': inactive_vendors_count,
        'active_services_count': active_services_count,
        'inactive_services_count': inactive_services_count,
        'suspended_vendors_count': suspended_vendors_count,
        'verified_vendors_count': verified_vendors_count,
        'vendors_with_services': vendors_with_services,
        'total_bill': total_bill,
        'total_credits': total_credits,
        'bugs_count': bugs_count
    }
    return render(request, "dashboard/cms/pages/dashboard.html", context)


@login_required
def profile_cms_view(request):
    user = get_cached_user(request, 'staff')
    context = {
        'cp': 'profile',
        'user': user
    }
    return render(request, 'user/cms/pages/profile.html', context)

@has_permission('admin')
def coupons_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'create_coupon' in request.POST:
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')

        discount_amount = request.POST.get('discount_amount')
        discount_amount = discount_amount if discount_amount else '0'

        discount_percentage = request.POST.get('discount_percentage')
        discount_percentage = discount_percentage if discount_percentage else '0'

        max_discount = request.POST.get('max_discount')
        max_discount = max_discount if max_discount else '0'

        is_active = request.POST.get('is_active') == 'on'
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        usage_limit = request.POST.get('usage_limit')
        usage_limit = usage_limit if usage_limit else '0'

        credits = request.POST.get('credits')
        credits = credits if credits else '0'

        skip_payment = request.POST.get('skip_payment') == 'yes'
        applicable_at = request.POST.getlist('applicable_at')

        coupon = Coupon.objects.create(
            name=name,
            code=code,
            description=description,
            discount_amount=discount_amount,
            discount_percentage=discount_percentage,
            max_discount=max_discount,
            is_active=is_active,
            start_date=start_date,
            end_date=end_date,
            usage_limit=usage_limit,
            credits=credits,
            skip_payment=skip_payment,
            applicable_at=applicable_at
        )
        messages.success(request, f'Coupon {coupon.name} with code {coupon.code} created successfully')
        return redirect('dashboard:Coupons')

    if request.method == 'POST' and 'update_coupon' in request.POST:
        coupon_id = request.POST.get('update_coupon')
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.name = request.POST.get('name')
        coupon.code = request.POST.get('code')
        coupon.description = request.POST.get('description')
        coupon.discount_amount = request.POST.get('discount_amount')
        coupon.discount_percentage = request.POST.get('discount_percentage')
        coupon.max_discount = request.POST.get('max_discount')
        coupon.is_active = request.POST.get('is_active') == 'on'
        coupon.start_date = request.POST.get('start_date')
        coupon.end_date = request.POST.get('end_date')
        coupon.usage_limit = request.POST.get('usage_limit')
        coupon.credits = request.POST.get('credits')
        coupon.skip_payment = request.POST.get('skip_payment') == 'yes'
        coupon.applicable_at = request.POST.getlist('applicable_at')
        coupon.save()
        messages.success(request, f'Coupon {coupon.name} with code {coupon.code} updated successfully')
        return redirect('dashboard:Coupons')
    
    if request.method == 'POST' and 'delete_coupon' in request.POST:
        coupon_id = request.POST.get('delete_coupon')
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.delete()
        messages.success(request, f'Coupon {coupon.name} with code {coupon.code} deleted successfully')
        return redirect('dashboard:Coupons')

    coupons = Coupon.objects.all().order_by('-created_at')
    for coupon in coupons:
        if coupon.start_date:
            coupon.update_start_date = coupon.start_date.strftime("%Y-%m-%d")
        if coupon.end_date:
            coupon.update_end_date = coupon.end_date.strftime("%Y-%m-%d")

    context = {
        'cp': 'pricings',
        'user': user,
        'coupons': coupons
    }
    return render(request, "dashboard/cms/pages/coupons.html", context)

@has_permission('admin')
def settings_cms_view(request):
    user = get_cached_user(request, 'staff')
    context = {
        'cp': 'settings',
        'user': user
    }
    return render(request, "dashboard/cms/pages/settings.html", context)


@has_permission('admin')
def pricings_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'add_pricing_tag' in request.POST:
        name = request.POST.get('name')
        tag = request.POST.get('tag')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        category = request.POST.get('category')
        description = request.POST.get('description')

        Pricing.objects.create(
            name=name,
            description=description,
            tag=tag,
            price=price,
            unit=unit,
            category=category
        )
        messages.success(request, 'Pricing created successfully')
        return redirect('dashboard:Pricings')
    
    if request.method == 'POST' and 'update_pricing_tag' in request.POST:
        id = request.POST.get('update_pricing_tag')
        name = request.POST.get('name')
        tag = request.POST.get('tag')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        category = request.POST.get('category')
        description = request.POST.get('description')

        pricing = get_object_or_404(Pricing, id=id)
        pricing.name = name
        pricing.description = description
        pricing.tag = tag
        pricing.price = price
        pricing.unit = unit
        pricing.category = category
        pricing.save()
        messages.success(request, 'Pricing updated successfully')
        return redirect('dashboard:Pricings')
    
    if request.method == 'POST' and 'delete_pricing_tag' in request.POST:
        id = request.POST.get('delete_pricing_tag')
        pricing = get_object_or_404(Pricing, id=id)
        pricing.delete()
        messages.success(request, 'Pricing deleted successfully')
        return redirect('dashboard:Pricings')

    pricing_tags = Pricing.objects.all()
    context = {
        'cp': 'pricings',
        'user': user,
        'pricing_tags': pricing_tags
    }
    return render(request, "dashboard/cms/pages/pricing.html", context)


@has_permission('admin, operations')
def vendors_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'verify_unverify_vendor' in request.POST:
        id = request.POST.get('verify_unverify_vendor')
        vendor = get_object_or_404(Vendor, id=id)
        if vendor.is_verified:
            vendor.is_verified = False
            messages.success(request, f'Vendor&nbsp; <strong>{vendor.name}</strong> &nbsp;unverified successfully')
        else:
            vendor.is_verified = True
            messages.success(request, f'Vendor&nbsp; <strong>{vendor.name}</strong> &nbsp;verified successfully')
        vendor.save()
        return redirect('dashboard:Vendors')
    
    if request.method == 'POST' and 'suspend_unsuspend_vendor' in request.POST:
        id = request.POST.get('suspend_unsuspend_vendor')
        vendor = get_object_or_404(Vendor, id=id)
        if vendor.is_suspended:
            vendor.is_suspended = False
            messages.success(request, f'Vendor&nbsp; <strong>{vendor.name}</strong> &nbsp;unsuspended successfully')
        else:
            vendor.is_suspended = True
            messages.success(request, f'Vendor&nbsp; <strong>{vendor.name}</strong> &nbsp;suspended successfully')
        vendor.save()
        return redirect('dashboard:Vendors')
    
    if request.method == 'POST' and 'delete_vendor' in request.POST:
        id = request.POST.get('delete_vendor')
        vendor = get_object_or_404(Vendor, id=id)
        vendor.delete()
        messages.success(request, f"Vendor {vendor.name} has been deleted successfully.")
        return redirect('dashboard:Vendors')
    
    if request.method == 'POST' and 'send_email_alert' in request.POST:
        email_purpose = request.POST.get('email_purpose')
        vendor_id = request.POST.get('send_email_alert')

        vendor = Vendor.objects.get(id=vendor_id)

        if vendor is None:
            messages.error(request, 'No vendor found')
            return redirect('dashboard:Vendors')
        
        if email_purpose == 'payment_reminder':
            subject = 'Payment Reminder'
            template = 'payment/emails/reminder.html'

            current_date = datetime.now().strftime("%b %d, %Y")
            current_year = datetime.now().year

            # Pay by will be the date from 5 days from the current date
            pay_by = (datetime.now() + timedelta(days=5)).strftime("%b %d, %Y")

            context = {
                'name': vendor.name,
                'amount': vendor.bill,
                'due_date': current_date,
                'pay_by': pay_by,
                'year': current_year
            }
            send_email_with_backend(
                subject=subject,
                template_name=template,
                context=context,
                email_info={
                    'from': "Payment Reminder Eventic <notification@eventic.in>",
                    'to': [vendor.email]
                },
                backend_name="info"
            )
        elif email_purpose == 'service_alert':
            subject = 'Service Alert'
            template = 'dashboard/cms/emails/service_alert.html'

            context = {
                'service_alert_message': vendor.get('service_alert_message')
            }
            send_email_with_backend(
                subject=subject,
                template_name=template,
                context=context,
                email_info={
                    'from': "Service Alert Eventic <notification@eventic.in>",
                    'to': [vendor.get('email')]
                },
                backend_name="info"
            )

        messages.success(request, 'Emails sent successfully')
        return redirect('dashboard:Vendors')
    
    vendors = Vendor.objects.annotate(
            leads_count=Count('leads', distinct=True),
            likes_count=Count('likes', distinct=True),
            saves_count=Count('saves', distinct=True),
        ).only('active_services', 'active_features', 'user__username', 'email', 'name', 'id', 'auto_bill_settlement_credits', 'is_active', 'is_suspended', 'is_verified', 'bill', 'credits').all()

    active_vendors = []
    verified_vendors = []
    suspended_vendors = []
    inactive_vendors = []
    pending_vendors = []
    number_service_vendors = []

    total_bill = 0
    total_credits = 0

    for vendor in vendors:
        if vendor.is_active:
            active_vendors.append(vendor)
        if vendor.is_verified:
            verified_vendors.append(vendor)
        if vendor.is_suspended:
            suspended_vendors.append(vendor)
        if not vendor.is_active:
            inactive_vendors.append(vendor)
        # Check vendor user has group pending_payment
        if vendor.user.groups.filter(name='pending_payment').exists():
            vendor.is_pending_payment = True
            pending_vendors.append(vendor)
        # Count the dictionary keys with the value True
        if True in vendor.active_services.values():
            vendor.active_services_count = sum(vendor.active_services.values())
            number_service_vendors.append(vendor)

        total_bill += vendor.bill
        total_credits += vendor.credits

    # Sort vendors by creation date
    vendors = sorted(vendors, key=lambda vendor: vendor.created_at, reverse=True)

    context = {
        'cp': 'users',
        'user': user,
        'vendors': vendors,
        'active_vendors': active_vendors,
        'verified_vendors': verified_vendors,
        'suspended_vendors': suspended_vendors,
        'inactive_vendors': inactive_vendors,
        'pending_vendors': pending_vendors,
        'number_service_vendors': number_service_vendors,
        'total_bill': total_bill,
        'total_credits': total_credits
    }
    return render(request, "dashboard/cms/pages/vendors.html", context)

@has_permission('admin, operations')
def users_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'delete_user' in request.POST:
        id = request.POST.get('delete_user')
        user = get_object_or_404(User, id=id)
        user.delete()
        messages.success(request, f"User {user.username} has been deleted successfully.")
        return redirect('dashboard:Users')
    
    users = User.objects.all()
    # Check if user is vendor
    for _user in users:
        if (_user.groups.filter(name='vendor').exists()):
            _user.is_vendor = True
            
        try:
            _user.phone = user.userprofile.phone
        except:
            _user.phone = None

    # Sort users by creation date
    users = sorted(users, key=lambda user: user.date_joined, reverse=True)

    context = {
        'cp': 'users',
        'user': user,
        'users': users
    }
    return render(request, "dashboard/cms/pages/users.html", context)

@has_permission('admin')
def staffs_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'delete_user' in request.POST:
        id = request.POST.get('delete_user')
        user = get_object_or_404(User, id=id)
        user.delete()
        messages.success(request, f"User {user.username} has been deleted successfully.")
        return redirect('dashboard:Staffs')
    
    staffs = User.objects.filter(is_staff=True)

    context = {
        'cp': 'users',
        'user': user,
        'staffs': staffs
    }
    return render(request, "dashboard/cms/pages/staffs.html", context)

@has_permission('admin, operations, developer')
def notifications_cms_view(request):
    user = get_cached_user(request, 'staff')

    if request.method == 'POST' and 'mark_all_as_read' in request.POST:
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        return redirect('dashboard:Notifications')
    
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as read.")
            return redirect('dashboard:Notifications')
        notification.is_read = True
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as read.')
        return redirect('dashboard:Notifications')

    if request.method == 'POST' and 'mark_as_unread' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as unread.")
            return redirect('dashboard:Notifications')
        notification.is_read = False
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as unread.')
        return redirect('dashboard:Notifications')
    
    if request.method == 'POST' and 'delete_notification' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if request.user != notification.user:
            messages.error(request, "You don't have permission to delete this notification.")
            return redirect('dashboard:Notifications')
        notification.delete()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, "Notification has been deleted successfully.")
        return redirect('dashboard:Notifications')

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
    return render(request, 'dashboard/cms/pages/notifications.html', context)


@has_permission('admin, developer')
def bugs_cms_view(request):
    user = get_cached_user(request, 'staff')
    
    if request.method == 'POST' and 'delete_bug' in request.POST:
        id = request.POST.get('delete_bug')
        bug = get_object_or_404(ErrorLog, id=id)
        bug.delete()
        messages.success(request, 'Bug deleted successfully')
        return redirect('dashboard:Bugs')
    
    bugs = ErrorLog.objects.all()

    # Sort the bugs by hit count
    bugs = bugs.order_by('-hit_count')
    context = {
        'cp': 'bugs',
        'bugs': bugs,  # All errors
        'user': user
    }
    return render(request, 'dashboard/cms/pages/bugs.html', context)



@has_permission('admin, operations')
def invitations_cms_view(request):
    user = get_cached_user(request, 'staff')
    invitations = InvitationModel.objects.all().order_by('-created_at')

    if request.method == "POST":
        if "update_status" in request.POST:
            invitation_id = request.POST.get("invitation_id")
            status = request.POST.get("status")
            invitation = get_object_or_404(InvitationModel, id=invitation_id)
            invitation.status = status
            invitation.save()
            messages.success(request, f"Invitation '{invitation.id}' status updated to {status}.")
            return redirect("dashboard:Invitations")

        if "delete_invitation" in request.POST:
            invitation_id = request.POST.get("invitation_id")
            invitation = get_object_or_404(InvitationModel, id=invitation_id)
            invitation.delete()
            messages.success(request, f"Invitation '{invitation.id}' deleted successfully.")
            return redirect("dashboard:Invitations")

    context = { 
        'cp': 'invitations',
        'invitations': invitations,
        'user': user,
    }
    return render(request, 'dashboard/cms/pages/invitations.html', context)


@has_permission('admin, operations')
def invitations_chart_data(request):
    filter_type = request.GET.get('filter', '7')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if filter_type == '7':
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif filter_type == '30':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif filter_type == 'month':
        start_date = datetime.now().replace(day=1)
        end_date = datetime.now()
    elif filter_type == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        return JsonResponse({'error': 'Invalid filter type or date range'}, status=400)

    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    all_dates_str = [date.strftime('%Y-%m-%d') for date in all_dates]

    invitations = InvitationModel.objects.filter(
        Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
    )

    active_invitations_per_day = {date: 0 for date in all_dates_str}
    inactive_invitations_per_day = {date: 0 for date in all_dates_str}
    invitations_per_day = {date: 0 for date in all_dates_str}

    for invitation in invitations:
        invitation_start = max(invitation.start_date, start_date.date())
        invitation_end = min(invitation.end_date, end_date.date())
        current_date = invitation_start
        while current_date <= invitation_end:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in active_invitations_per_day:
                active_invitations_per_day[date_str] += 1
            current_date += timedelta(days=1)

        # Increment invitations per day for the start date
        start_date_str = invitation.start_date.strftime('%Y-%m-%d')
        if start_date_str in invitations_per_day:
            invitations_per_day[start_date_str] += 1

        # Mark as inactive only on the end date
        end_date_str = invitation.end_date.strftime('%Y-%m-%d')
        if end_date_str in inactive_invitations_per_day and invitation.status in ['expired', 'suspended']:
            inactive_invitations_per_day[end_date_str] += 1

    return JsonResponse({
        'labels': all_dates_str,
        'invitations_per_day': [invitations_per_day[date] for date in all_dates_str],
        'active_invitations_per_day': [active_invitations_per_day[date] for date in all_dates_str],
        'inactive_invitations_per_day': [inactive_invitations_per_day[date] for date in all_dates_str]
    })


@has_permission('admin, operations')
def templates_cms_view(request):
    user = get_cached_user(request, 'staff')

    # Prefetch related data for templates
    templates = TemplateModel.objects.annotate(
        sold_count=Count('invitations', filter=Q(invitations__is_paid=True)),
        review_count=Count('reviews', distinct=True)
    ).order_by('-created_at')

    # Total count of sold templates
    sold_templates_count = templates.filter(sold_count__gt=0).count()

    # Top 5 most sold templates
    most_sold_templates = templates.order_by('-sold_count')[:5]

    # Top 5 most reviewed templates
    most_reviewed_templates = templates.order_by('-review_count')[:5]

    if request.method == "POST":
        if "update_status" in request.POST:
            template_id = request.POST.get("template_id")
            status = request.POST.get("status")
            template = get_object_or_404(TemplateModel, id=template_id)
            template.active = True if status == "approved" else False
            template.save()
            messages.success(request, f"Template '{template.name}' status updated to {status}.")
            return redirect("dashboard:Templates")

        if "delete_template" in request.POST:
            template_id = request.POST.get("template_id")
            template = get_object_or_404(TemplateModel, id=template_id)
            template.delete()
            messages.success(request, f"Template '{template.name}' deleted successfully.")
            return redirect("dashboard:Templates")

        if "edit_template" in request.POST:
            template_id = request.POST.get("template_id")
            template = get_object_or_404(TemplateModel, id=template_id)
            template.name = request.POST.get("name")
            template.description = request.POST.get("description")
            template.price = request.POST.get("price")
            template.free_days = request.POST.get("free_days")
            template.tag = request.POST.get("tag")
            if "thumbnail" in request.FILES:
                template.thumbnail = request.FILES.get("thumbnail")
            template.save()
            messages.success(request, f"Template '{template.name}' updated successfully.")
            return redirect("dashboard:Templates")

    context = {
        'cp': 'templates',
        'templates': templates,
        'sold_templates_count': sold_templates_count,
        'most_sold_templates': most_sold_templates,
        'most_reviewed_templates': most_reviewed_templates,
        'user': user,
    }
    return render(request, 'dashboard/cms/pages/templates.html', context)





@has_permission('admin')
def edit_template(request, template_id):
    template = get_object_or_404(TemplateModel, id=template_id)
    if request.method == "POST":
        template.name = request.POST.get("name")
        template.description = request.POST.get("description")
        template.price = request.POST.get("price")
        template.free_days = request.POST.get("free_days")
        template.tag = request.POST.get("tag")
        
        if "thumbnail" in request.FILES:
            thumbnail = request.FILES.get("thumbnail")
            if not template.thumbnail or thumbnail.name != template.thumbnail.split('/')[-1]:
                if template.thumbnail:
                    default_storage.delete(template.thumbnail)
                thumbnail.name = f"{uuid4()}.{thumbnail.name.split('.')[-1]}"
                thumbnail = default_storage.save(f'templates/{thumbnail.name}', thumbnail)
                template.thumbnail = default_storage.url(thumbnail)
        
        if "template_invite_card" in request.FILES:
            template_invite_card = request.FILES.get("template_invite_card")
            if not template.info.get('invite_card') or template_invite_card.name != template.info['invite_card'].split('/')[-1]:
                if template.info.get('invite_card'):
                    default_storage.delete(template.info['invite_card'])
                template_invite_card.name = f"{uuid4()}.{template_invite_card.name.split('.')[-1]}"
                template_invite_card = default_storage.save(f'templates/{template_invite_card.name}', template_invite_card)
                template.info['invite_card'] = default_storage.url(template_invite_card)
        
        template.save()
        messages.success(request, f"Template '{template.name}' updated successfully.")
        return redirect("dashboard:Templates")
    return render(request, "dashboard/cms/pages/edit_template.html", {"template": template})


@has_permission('admin, operations')
def templates_analytics_view(request):
    user = get_cached_user(request, 'staff')
    template_id = request.GET.get('template_id')

    if not template_id:
        messages.error(request, "Template ID is required.")
        return redirect('dashboard:Templates')

    template = get_object_or_404(TemplateModel.objects.prefetch_related('reviews'), id=template_id)

    if request.method == "POST":
        if "pin_review" in request.POST:
            review_id = request.POST.get("review_id")
            review = get_object_or_404(Review, id=review_id)
            pinned_reviews_count = Review.objects.filter(template=review.template, pinned=True).count()

            if not review.pinned and pinned_reviews_count >= 3:
                messages.error(request, "Only 3 reviews can be pinned per template.")
            else:
                review.pinned = not review.pinned
                review.save()
                messages.success(request, f"Review {'pinned' if review.pinned else 'unpinned'} successfully.")

            return redirect(request.path + f"?template_id={template_id}")

        if "delete_review" in request.POST:
            review_id = request.POST.get("review_id")
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            messages.success(request, "Review deleted successfully.")
            return redirect(request.path + f"?template_id={template_id}")

    context = {
        'cp': 'templates',
        'template': template,
        'user': user,
    }
    return render(request, 'dashboard/cms/pages/templates_analytics.html', context)

@has_permission('admin, operations')
def template_reviews_view(request, template_id):
    template = get_object_or_404(TemplateModel.objects.prefetch_related('reviews'), id=template_id)

    if request.method == "POST":
        if "pin_review" in request.POST:
            review_id = request.POST.get("review_id")
            review = get_object_or_404(Review, id=review_id)
            review.pinned = not review.pinned
            review.save()
            messages.success(request, f"Review {'pinned' if review.pinned else 'unpinned'} successfully.")
            return redirect('dashboard:TemplateReviews', template_id=template_id)

        if "delete_review" in request.POST:
            review_id = request.POST.get("review_id")
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            messages.success(request, "Review deleted successfully.")
            return redirect('dashboard:TemplateReviews', template_id=template_id)

    context = {
        'template': template,
    }
    return render(request, 'invitation/cms/pages/reviews.html', context)

@has_permission('admin, operations')
def invitations_analytics_data(request):
    active_invitations = InvitationModel.objects.filter(
        start_date__lte=datetime.now(), end_date__gte=datetime.now(), status='active'
    ).count()
    inactive_invitations = InvitationModel.objects.filter(
        Q(status__in=['expired', 'suspended']) | Q(end_date__lt=datetime.now().date())
    ).count()
    avg_duration = InvitationModel.objects.annotate(
        duration=F('end_date') - F('start_date')
    ).aggregate(Avg('duration'))['duration__avg']
    total_reports = TemplateModel.objects.count() + ReportReview.objects.count()

    return JsonResponse({
        'active_invitations': active_invitations,
        'inactive_invitations': inactive_invitations,
        'avg_duration': avg_duration.days if avg_duration else 0,
        'total_reports': total_reports,
    })

@has_permission('admin, operations')
def templates_heatmap_data(request):
    template_id = request.GET.get('template_id')
    if not template_id:
        return JsonResponse({'error': 'Template ID is required'}, status=400)

    # Filter invitations by template ID
    invitations = InvitationModel.objects.filter(template_id=template_id)

    # Aggregate data by country
    country_data = {}
    for invitation in invitations:
        country_code = invitation.details.get('venueLocation', {}).get('countryCode', 'Unknown')
        if country_code not in country_data:
            country_data[country_code] = 0
        country_data[country_code] += 1

    # Prepare heatmap points and location data
    heatmap_points = []
    locations = []
    for country_code, count in country_data.items():
        # Map country code to latitude and longitude (example coordinates, replace with actual data)
        coordinates = COUNTRY_COORDINATES.get(country_code, {'lat': 0, 'lng': 0})
        heatmap_points.append([coordinates['lat'], coordinates['lng'], count])
        locations.append({'lat': coordinates['lat'], 'lng': coordinates['lng'], 'count': count, 'country_code': country_code})

    return JsonResponse({
        'heatmap_points': heatmap_points,
        'locations': locations
    })

# Example mapping of country codes to coordinates (replace with actual data)
COUNTRY_COORDINATES = {
    'US': {'lat': 37.0902, 'lng': -95.7129},
    'IN': {'lat': 20.5937, 'lng': 78.9629},
    'UK': {'lat': 55.3781, 'lng': -3.4360},
    'Unknown': {'lat': 0, 'lng': 0}
}

