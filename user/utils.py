def get_cached_user(request, priority="user"):
    # user = request.user
    # user = cache.get(f'cached_user_{request.user.id}')
    if request.user.is_anonymous:
        return request.user
    
    user = request.user
    user.priority = priority

    if priority == "user":
        if 'vendor' in user.groups.values_list('name', flat=True):
            user.has_group_vendor = True

        if 'pending_payment' in user.groups.values_list('name', flat=True):
            user.has_group_pending_payment = True

    if priority == "vendor" and 'vendor' in user.groups.values_list('name', flat=True):
        user.is_vendor = True
        user.vendor_id = user.vendor.id
        user.vendor_is_active = user.vendor.is_active
        user.vendor_is_verified = user.vendor.is_verified
        user.vendor_is_suspended = user.vendor.is_suspended

    if priority == "staff" and user.is_staff:
        if 'developer' in user.groups.values_list('name', flat=True):
            user.is_developer = True

        if 'operations' in user.groups.values_list('name', flat=True):
            user.is_operations = True
        
        if 'admin' in user.groups.values_list('name', flat=True):
            user.is_admin = True
        
    if user.is_superuser:
        user.is_admin = True
        user.is_staff = True

    try:
        user.profile_picture = user.userprofile.picture
        user.phone = user.userprofile.phone
    except:
        user.profile_picture = None
        user.phone = None
            
        # cache.set(f'cached_user_{request.user.id}', user, 60 * 60 * 24)  # Cache for 24 hours
    return user