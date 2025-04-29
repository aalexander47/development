from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_backends
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from .decorators import is_not_member
from .utils import add_group_to_user
from core.utils import send_email_with_backend
from user.models import UserProfile, Notification
from vendor.models import Vendor
from django.conf import settings
import random
import string
import re
from cryptography.fernet import Fernet

key = settings.FERNET_KEY
cipher_suite = Fernet(key)

def auth_redirect_view(request):
    if request.user.is_anonymous:
        return redirect('auth:login')
    
    next_url = request.GET.get('next', "")
    if next_url and next_url != 'auth:logout' and next_url != 'auth:login':
        return redirect(next_url)

    if request.user.groups.filter(name="vendor").exists():
        return redirect('vendor:Dashboard')
    
    if request.user.groups.filter(name="pending_payment").exists():
        return redirect('payment:business_registration_payment')
    
    if request.user.is_staff:
        return redirect('dashboard:Dashboard')
    
    if request.user.is_superuser:
        return redirect('admin:index')
    
    # Redirect to the next page

    return redirect('user:Profile')


def login_request(request):
    if request.user.is_authenticated:
        return redirect('auth:auth_redirect_view')
    
    if request.method == 'POST':
        username_email_phone = request.POST.get('username_email_phone', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Login with email, username, or phone
        user = User.objects.filter(
            Q(username=username_email_phone) |
            Q(email=username_email_phone) |
            Q(userprofile__phone=username_email_phone)
        ).first()
        
        if not user:
            messages.error(request, 'Invalid username, email, or phone number.')
            login_data = {
                'username_email_phone': username_email_phone,
                'password': password
            }
            return render(request, 'authenticator/login.html', login_data)
        
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            next_url = request.GET.get('next', "")
            if next_url and next_url not in ['auth:logout', 'auth:login']:
                return redirect(next_url)
            return redirect('auth:auth_redirect_view')
        else:
            messages.error(request, 'Invalid username, email, phone, or password.')
            login_data = {
                'username_email_phone': username_email_phone,
                'password': password
            }
            return render(request, 'authenticator/login.html', login_data)
    
    return render(request, 'authenticator/login.html')


def signup_request(request):
    if request.user.is_authenticated:
        return redirect('auth:auth_redirect_view')
    
    signup_data = {}
    errors = {
        'first_name': [],
        'last_name': [],
        'username': [],
        'email': [],
        'phone': [],
        'password': [],
        'general': []
    }
    
    if request.method == 'POST' and "signup" in request.POST:
        # Collect POST data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

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
            username = username.strip()
            # Check if any special characters are present or spaces. Special characters exclude underscores and dots.
            if not re.match(r'^[a-zA-Z0-9_.]{3,}$', username):
                errors['username'].append("Username must be at least 3 characters and contain only letters, numbers, dot, and underscores.")
                check_errors = True
        
        # Email Validation
        if not email:
            errors['email'].append("Email is required.")
            check_errors = True
        
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            errors['email'].append("Invalid email format.")
            check_errors = True

        if User.objects.filter(email=email).exists():
            errors['email'].append("Email is already in use.")
            check_errors = True
        
        # Phone Validation
        if not phone:
            errors['phone'].append("Phone number is required.")
            check_errors = True
        
        if not re.match(r'^\d{10}$', phone):
            errors['phone'].append("Invalid phone number format.")
            check_errors = True

        if UserProfile.objects.filter(phone=phone).exists():
            errors['phone'].append("Phone number is already in use.")
            check_errors = True
        
        # Password Validation
        if not password:
            errors['password'].append("Password is required.")
            check_errors = True
        
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
            errors['password'].append("Password must be at least 8 characters")
            errors['password'].append("Contain at least one uppercase letter")
            errors['password'].append("Contain at least one lowercase letter")
            errors['password'].append("Contain at least one number")
            errors['password'].append("Contain at least one special character")
            check_errors = True

        if check_errors:
            # Populate context for re-rendering
            signup_data = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'phone': phone,
                'password': password
            }
            return render(request, 'authenticator/signup.html', {**signup_data, 'errors': errors})
        
        # Populate context for re-rendering
        signup_data = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'phone': phone,
            'password': password
        }
        
        # Proceed with user creation if no errors
        if not check_errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(user=user, phone=phone)

                # Explicitly set the backend
                login(request, user)

                messages.success(request, 'User registered successfully.')
                next_url = request.GET.get('next', "")
                if next_url:
                    return redirect(next_url)
                return redirect('auth:auth_redirect_view')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        
        # Add a generic error if user creation fails
        if not request.user:
            errors['general'].append("An error occurred while creating your account. Please try again.")
    
    # Render template with errors and data
    return render(request, 'authenticator/signup.html', {**signup_data, 'errors': errors})


def temp_signup(request):
    if request.user.is_authenticated:
        return redirect('auth:auth_redirect_view')
    
    signup_data = {}
    next_url = request.GET.get("next", "/invitation/")
    
    if request.method == 'POST' and "signup" in request.POST:
        # Collect POST data
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()


        # Auto generate strong password

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please try again.')
            return redirect(next_url)
        
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists. Please try again.')
            return redirect(next_url)

        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Populate context for re-rendering
        signup_data = {
            'email': email,
            'phone': phone,
            'password': password
        }

        username = email.split('@')[0]

        # encrypt the email
        encrypted_key = cipher_suite.encrypt(email.encode())

        report_user_url = f"https://eventic.in/user/report/{encrypted_key}"
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            UserProfile.objects.create(user=user, phone=phone)

            # Explicitly set the backend
            login(request, user)
            
            settings.THREAD_POOL_EXECUTOR.submit(
                send_email_with_backend,
                subject='Account Created Successfully',
                template_name='authenticator/emails/signup.html',
                email_info={
                    'from': "Eventic <company@eventic.in>",
                    'to': [email]
                },
                context={
                    "report_user_url": report_user_url,
                    "password": password
                },
                backend_name="default"
            )

            messages.success(request, 'User registered successfully.')
            if next_url:
                return redirect(next_url)
            return redirect('auth:auth_redirect_view')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        
    # Render template with errors and data
    return redirect(next_url)


@login_required(login_url='auth:login')
def logout_request(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('auth:login')


@is_not_member('vendor, pending_payment, staff')
def business_registration(request): 
    if request.method == "POST" and 'business_name' in request.POST:
        business_name = request.POST.get("business_name").strip()

        if business_name:
            success, msg = add_group_to_user(request.user, "vendor")
            success = True
            if success:
                Vendor.objects.create(user=request.user, name=business_name, phone=request.user.userprofile.phone, email=request.user.email)
                # Get all the staff users and send them the notification
                staff_users = User.objects.filter(is_staff=True, groups__name='admin')
                notifications = []
                for staff_user in staff_users:
                    notifications.append(
                        Notification(
                            user=staff_user, 
                            title=f"New Vendor Registration",
                            type="business_registration",
                            description=f"Business name: {business_name}, Registered vendor has payment pending.",
                            other={
                                "user_id": request.user.id,
                                "business_name": business_name,
                                "email": request.user.email,
                                'phone': request.user.userprofile.phone,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name
                            }
                        )
                    )
                
                with transaction.atomic():
                    Notification.objects.bulk_create(notifications)
                messages.success(request, 'ᵔᴥᵔ Business registered successfully.')
            else:
                messages.error(request, "An error occurred while creating your business. Please try again.")
            return redirect('auth:auth_redirect_view')

        messages.error(request, 'Error occurred while creating your business. Please try again.')
        return redirect('auth:business_registration')
    
    return render(request, 'authenticator/business-registration.html')