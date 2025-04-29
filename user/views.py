from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, Notification
from invitation.models import Invitation as UserInvitation
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.contrib import messages
from uuid import uuid4
from .utils import get_cached_user
# Removed unused imports
from django.core.files.images import get_image_dimensions
import re


# Create your views here.
@login_required
def profile_cms_view(request):
    user = get_cached_user(request)

    if request.method == 'POST' and 'update_user_details' in request.POST:
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        profile_picture = request.FILES.get('profile_picture', None)
        file_exists = request.POST.get('file_exists')

        errors = {
            'first_name': [],
            'last_name': [],
            'username': [],
            'email': [],
            'phone': [],
            'general': [],
            'profile_picture': []
        }
        check_errors = False

        # Check for errors
        # First name and last name Validation
        if not first_name:
            errors['first_name'].append("First name is required.")
            check_errors = True
        
        if not last_name:
            errors['last_name'].append("Last name is required.")
            check_errors = True
        
        # Username Validation
        if not username:
            errors['username'].append("Username is required.")
            check_errors = True
        elif username:
            # Check if any special characters are present or spaces. Special characters exclude underscores and dots.
            if not re.match(r'^[a-zA-Z0-9_.]{3,}$', username):
                errors['username'].append("Username must be at least 3 characters and contain only letters, numbers, dot, and underscores.")
                check_errors = True

            if username != user.username:
                if User.objects.filter(username=username).exists():
                    errors['username'].append(f"Username {username} is already in use.")
                    check_errors = True
        
        # Email Validation
        if not email:
            errors['email'].append("Email is required.")
            check_errors = True
        
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            errors['email'].append("Invalid email format.")
            check_errors = True

        if email != user.email:
            if User.objects.filter(email=email).exists():
                errors['email'].append(f"Email {email} is already in use.")
                check_errors = True
        
        # Phone Validation
        if not phone:
            errors['phone'].append("Phone number is required.")
            check_errors = True
        
        if not re.match(r'^\d{10}$', phone):
            errors['phone'].append("Invalid phone number format.")
            check_errors = True

        if phone != user.phone:
            if UserProfile.objects.filter(phone=phone).exists():
                errors['phone'].append(f"Phone number {phone} is already in use.")
                check_errors = True
    
        if profile_picture:
            if profile_picture.size > 500 * 1024:
                errors['profile_picture'].append("Profile picture size must be less than 500 KB.")
                check_errors = True
            try:
                width, height = get_image_dimensions(profile_picture)
                if width != height:
                    errors['profile_picture'].append("Profile picture must be in a 1:1 ratio.")
                    check_errors = True
            except Exception:
                errors['profile_picture'].append("Invalid image file.")
                check_errors = True
                
        if check_errors:
            return render(request, 'user/cms/pages/profile.html', {'cp': 'profile', 'user': user, 'errors': errors})

        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)  # Ignored 'created' as it's unused

        if file_exists == "removed":
            if user_profile.picture and default_storage.exists(user_profile.picture.name):
                default_storage.delete(user_profile.picture.name)
            user_profile.picture = ""

        if file_exists == "changed" and profile_picture:
            if user_profile.picture and default_storage.exists(user_profile.picture.name):
                default_storage.delete(user_profile.picture.name)

            profile_picture.name = f'eventic-{username.lower()}-{uuid4().hex[:4]}.{profile_picture.name.split(".")[-1]}'
            user_profile.picture = profile_picture

        user_profile.save()

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        messages.success(request, 'User details updated successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'user:Profile'))

    if request.method == 'POST' and 'change_password' in request.POST:
        old_password = request.POST.get("old_password", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        errors = []
        
        # Password Validation
        if not re.match(r'^(?=.[a-z])(?=.[A-Z])(?=.\d)(?=.[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$', new_password):
            errors.append("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.")

        if new_password != confirm_password:
            errors.append("New passwords do not match.")
        
        elif not user.check_password(old_password):
            errors.append("Old password is incorrect.")

        if errors:
            return render(request, 'user/cms/pages/profile.html', {'cp': 'profile', 'user': user, 'pwd_errors': errors})

        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password changed successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'user:Profile'))

    context = {
        'cp': 'profile',
        'user': user,
    }
    return render(request, 'user/cms/pages/profile.html', context)


@login_required
def likes_cms_view(request):
    user = get_cached_user(request)
    service_likes_count = user.likes.filter(content_type__model='service').count()
    template_likes_count = user.template_likes.count()

    context = {
        'cp': 'likes',
        'service_likes_count': service_likes_count,
        'template_likes_count': template_likes_count,
        'user': user
    }
    return render(request, 'user/cms/pages/likes.html', context)


@login_required
def likes_service_view(request):
    user = get_cached_user(request)
    user_likes = user.likes.select_related('content_type').prefetch_related('content_object')
    liked_services = [
        {
            "slug": f"/{like.content_type.app_label}/service/{like.content_object.id}/" + re.sub(r'[^\w-]', '', like.content_object.vendor.name.lower().replace(' ', '-')),
            "service": like.content_object.service,
            "app_label": like.content_type.app_label
        }
        for like in user_likes if hasattr(like.content_object, 'vendor')
    ]
    return render(request, 'user/cms/pages/likes_service.html', {'liked_services': liked_services, 'cp': 'likes'})


@login_required
def likes_template_view(request):
    user = get_cached_user(request)
    liked_templates = user.template_likes.select_related('template')
    liked_templates_data = [
        {
            "id": like.template.id,
            "name": like.template.name,
            "description": like.template.description,
            "thumbnail": like.template.thumbnail,
            "slug": f"/invitation/template/{like.template.id}/"
        }
        for like in liked_templates
    ]
    return render(request, 'user/cms/pages/likes_template.html', {'liked_templates': liked_templates_data, 'cp': 'likes'})


@login_required
def saves_cms_view(request):
    user = get_cached_user(request)
    saved_services_count = user.saves.filter(content_type__model='service').count()
    saved_templates_count = user.template_saves.count()

    context = {
        'cp': 'saves',
        'saved_services_count': saved_services_count,
        'saved_templates_count': saved_templates_count,
        'user': user
    }
    return render(request, 'user/cms/pages/saves.html', context)


@login_required
def saves_service_view(request):
    user = get_cached_user(request)
    user_saves = user.saves.select_related('content_type').prefetch_related('content_object')
    saved_services = [
        {
            "slug": f"/{save.content_type.app_label}/service/{save.content_object.id}/" + re.sub(r'[^\w-]', '', save.content_object.vendor.name.lower().replace(' ', '-')),
            "service": save.content_object.service,
            "app_label": save.content_type.app_label

        }
        for save in user_saves if hasattr(save.content_object, 'vendor')
    ]
    return render(request, 'user/cms/pages/saves_service.html', {'saved_services': saved_services, 'cp': 'saves'})


@login_required
def saves_template_view(request):
    user = get_cached_user(request)
    saved_templates = user.template_saves.select_related('template')
    saved_templates_data = [
        {
            "id": save.template.id,
            "name": save.template.name,
            "description": save.template.description,
            "thumbnail": save.template.thumbnail,
            "slug": f"/invitation/template/{save.template.id}/"
        }
        for save in saved_templates
    ]
    return render(request, 'user/cms/pages/saves_template.html', {'saved_templates': saved_templates_data, 'cp': 'saves'})


@login_required
def notifications_cms_view(request):
    user = get_cached_user(request)

    if request.method == 'POST' and 'mark_all_as_read' in request.POST:
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        return redirect('user:Notifications')
    
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as read.")
            return redirect('user:Notifications')
        notification.is_read = True
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as read.')
        return redirect('user:Notifications')

    if request.method == 'POST' and 'mark_as_unread' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if user != notification.user:
            messages.error(request, "You don't have permission to mark this notification as unread.")
            return redirect('user:Notifications')
        notification.is_read = False
        notification.save()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, 'Notification marked as unread.')
        return redirect('user:Notifications')
    
    if request.method == 'POST' and 'delete_notification' in request.POST:
        id = request.POST.get('notification_id', '')
        notification = get_object_or_404(Notification, id=id)
        if request.user != notification.user:
            messages.error(request, "You don't have permission to delete this notification.")
            return redirect('user:Notifications')
        notification.delete()
        # Invalidate the cache
        cache_notification_key = f'cached_notifications_{user.id}'
        cache_count = f'notification_count_{user.id}'
        cache.delete(cache_notification_key)
        cache.delete(cache_count)
        messages.success(request, "Notification has been deleted successfully.")
        return redirect('user:Notifications')

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
    return render(request, 'user/cms/pages/notifications.html', context)


@login_required
def invitations_cms_view(request):
    user = get_cached_user(request)
    invitations = UserInvitation.objects.filter(user=user)
    _data = {'cp': 'invitations', 'user': user ,'invitations': invitations}
    return render(request, 'user/cms/pages/invitations.html', _data)