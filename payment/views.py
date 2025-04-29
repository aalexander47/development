from django.shortcuts import render, redirect
from django.db import transaction
from django.conf import settings
from .models import Payment, Transaction
from .tasks import send_payment_reminder_email
from core.utils import send_email_with_backend
from dashboard.models import Pricing, Coupon
from vendor.models import Vendor, TrackBilling, AppliedCoupon, AppliedReferral
from vendor.utils import referral_code_to_account_id
from django.db.models import Exists, OuterRef
import razorpay
from authenticator.decorators import has_permission
from authenticator.utils import add_group_to_user, remove_group_from_user
from django.contrib import messages
from datetime import datetime, timedelta, date
import calendar
from decimal import Decimal
import uuid

@has_permission('pending_payment')
def handle_payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        payment_type = request.POST.get('payment_type', '')

        if not request.user.is_authenticated:
            return redirect('auth:auth_redirect_view')
        
        user_id = request.user.id

        # Save order details in the database
        payment = Payment(
            order_id=order_id,
            status='CREATED',
            payment_id=payment_id, 
        )
        payment.user_id = user_id
        payment.save()

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        credit_plans = {
            'basic': {
                'price': 1000,
                'credits': 1000
            },
            'standard': {
                'price': 2250,
                'credits': 2500
            },
            'premium': {
                'price': 4500,
                'credits': 5000
            }
        }

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(params_dict)
            if payment_type == 'BR_payment':
                remove_group_from_user(request.user, 'pending_payment')
                add_group_to_user(request.user, 'vendor')
                vendor = Vendor.objects.get(user_id=user_id)
                vendor.credits = 500
                vendor.save()
                Transaction.objects.create(user=request.user, transaction_type='credit', amount=500, method='point', description='Business registration welcome credits')
                payment.amount = 99
                payment.status = 'SUCCESS'
                payment.save(description='Business registration payment.')
                
                user_name = f"{request.user.first_name} {request.user.last_name}" if request.user.first_name and request.user.last_name else request.user.username
                messages.success(request, 'ᵔᴥᵔ Business registered successfully. Hurrah!')
                messages.success(request, 'You have got &nbsp;<strong>₹500/-</strong>&nbsp; worth of credits to start your business.')
                settings.THREAD_POOL_EXECUTOR.submit(
                    send_email_with_backend,
                    subject='Business Registration Successful. Welcome to Eventic!',
                    template_name='authenticator/emails/welcome.html',
                    context={
                        'user_name': user_name
                    },
                    email_info={
                        'from': "Eventic <company@eventic.in>",
                        'to': [request.user.email]
                    },
                    backend_name="default"
                )
                return redirect('auth:auth_redirect_view')
            
            if payment_type == 'vendor_bill_settlement_payment':
                vendor = Vendor.objects.get(user_id=user_id)
                payment.amount = vendor.bill
                payment.status = 'SUCCESS'
                payment.save(description='Vendor bill settlement payment.')
                vendor.bill = 0
                vendor.bill_payment_alert_count = 0
                vendor.save()
                messages.success(request, 'Bill settled successfully')
                settings.THREAD_POOL_EXECUTOR.submit(
                    send_email_with_backend,
                    subject='Bill settled successfully',
                    template_name='vendor/emails/bill_settled.html',
                    context={
                        'vendor': vendor
                    },
                    email_info={
                        'from': "Eventic <notification@eventic.in>",
                        'to': [request.user.email]
                    },
                    backend_name="info"
                )
                return redirect('vendor:Billing')
            
            if payment_type in credit_plans:
                amount = credit_plans[(payment_type).lower()]['price']
                credit = credit_plans[(payment_type).lower()]['credits']

                vendor = Vendor.objects.get(user_id=user_id)
                Transaction.objects.create(
                    user_id=user_id,
                    amount= credit,
                    transaction_type='credit',
                    method = 'point',
                    description= f'Bought a {payment_type} credit plan ({credit} credits) for Rs.{amount}/-.',
                    razorpay_payment_id = payment.payment_id
                )
                payment.amount = amount
                payment.status = 'SUCCESS'
                payment.save(description='Credit payment.')
                vendor.credits += credit
                vendor.save()
                messages.success(request, f'Congrats! Payment successful. {credit} credits added to your account.')
                messages.success(request, f'Bought a {payment_type} credit plan ({credit} credits) for Rs.{amount}/-.')
                return redirect('vendor:Billing')
            
        except Exception as e:
            payment.status = 'FAILED'
            payment.save(description='Payment failed.')
            if payment_type == 'BR_payment':
                return render(request, 'payment/BR_payment_failed.html')
            elif payment_type == 'vendor_bill_settlement_payment':
                return render(request, 'payment/bill_settlement_payment_failed.html')
    return redirect('auth:auth_redirect_view')


@has_permission("pending_payment")
def business_registration_payment(request):
    price = 99
    context = create_rezorpay_payment(amount=price, payment_type='BR_payment') # 99 INR
    context['price'] = price
    return render(request, 'payment/business_registration_payment.html', context)

@has_permission('vendor, pending_payment')
def apply_code(request):
    user = request.user
    if request.method == 'POST' and 'apply_code' in request.POST:
        _code = request.POST.get('apply_code', '')
        # Get the previous page path only the route not domain or query params
        page_path = request.META.get('HTTP_REFERER', 'vendor:Billing').split(request.get_host())[1].split('?')[0]

        # Check the coupon code exists
        if not _code:
            messages.error(request, 'Please enter a valid coupon code.')
            return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))
        
        _coupon = Coupon.objects.filter(code=_code).first()
        referred_by = Vendor.objects.filter(account_id=referral_code_to_account_id(_code), is_active=True, is_suspended=False).first()

        if not _coupon and not referred_by:
            messages.error(request, 'Invalid code.')
            return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))
        
        _code_type = None
        
        # Check if the coupon code is referral code or coupon code
        if _coupon is not None:
            _code_type = 'coupon'
        
        if referred_by is not None:
            _code_type = 'referral'

        if _code_type is not None:
            if _code_type == 'coupon':
                vendor = Vendor.objects.annotate(
                    has_coupon_code=Exists(AppliedCoupon.objects.filter(vendor=OuterRef('pk'), coupon=_coupon))
                ).only('account_id', 'is_active', 'is_suspended', 'credits').get(user=user)

                if page_path == '/vendor/billing/' and not vendor.is_active:
                    messages.error(request, 'Your account is not active. Please update your business details.To redeem apply code.')
                    return redirect('vendor:Details')
            
                if page_path == '/vendor/billing/' and vendor.is_suspended:
                    messages.error(request, 'Your account is suspended. Please contact support for more information.')
                    return redirect('vendor:Dashboard')
                
                if not _coupon.is_valid():
                    messages.error(request, 'Coupon is not valid. Coupon may be expired or inactive.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if page_path == '/vendor/billing/' and 'redemption' not in _coupon.applicable_at:
                    messages.error(request, 'Coupon is not applicable for redemption.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if _coupon.usage_limit and _coupon.usage_count >= _coupon.usage_limit:
                    # Coupon usage limit reached inactivate the coupon
                    _coupon.is_active = False
                    _coupon.save()
                    messages.error(request, 'Coupon usage limit reached.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))
                
                _info = {
                    'credits': _coupon.credits,
                    'usage_limit': _coupon.usage_limit,
                    'user_number': _coupon.usage_count + 1
                }
                _coupon.usage_count += 1

                if _coupon.credits:
                    vendor.credits += _coupon.credits
                    vendor.save()

                AppliedCoupon.objects.create(
                    coupon=_coupon, 
                    vendor=vendor, 
                    code=_coupon.code, 
                    info=_info
                )

                Transaction.objects.create(
                    user=user, 
                    transaction_type='credit', 
                    amount=_coupon.credits, 
                    method='point', 
                    description=f'Applied coupon code: {_coupon.code}. Credits: {_coupon.credits}.'
                )

                if page_path == '/payment/business-registration-payment/' and _coupon.skip_payment and 'registration' in _coupon.applicable_at:
                    messages.success(request, 'Coupon applied successfully.')
                    # Remove pending_payment group from the user
                    remove_group_from_user(user, 'pending_payment')
                    add_group_to_user(user, 'vendor')
                    user.save()
                    
                    messages.success(request, 'ᵔᴥᵔ Business registered successfully. Hurrah!')
                    messages.success(request, 'You have saved &nbsp;<strong>₹99/-</strong>&nbsp; registration fee. And also get &nbsp;<strong>₹500/-</strong>&nbsp; worth of credits to start your business.')
                    
                    user_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else vendor.name
                    settings.THREAD_POOL_EXECUTOR.submit(
                        send_email_with_backend,
                        subject='Business Registration Successful. Welcome to Eventic!',
                        template_name='authenticator/emails/welcome.html',
                        context={
                            'user_name': user_name
                        },
                        email_info={
                            'from': "Eventic <company@eventic.in>",
                            'to': [request.user.email]
                        },
                        backend_name="default"
                    )
                    return redirect('vendor:Dashboard')
                
                if page_path == '/payment/business-registration-payment/' and not _coupon.skip_payment and 'registration' in _coupon.applicable_at:
                    messages.success(request, 'Coupon applied successfully. Please complete the payment.')
                    return redirect('payment:business_registration_payment')

                messages.success(request, 'Coupon applied successfully.')
                return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))
        
            elif _code_type == 'referral':
                vendor = Vendor.objects.annotate(
                    has_referral_code=Exists(AppliedReferral.objects.filter(vendor=OuterRef('pk'), code=_code)),
                    has_refered=Exists(AppliedReferral.objects.filter(referred_by=OuterRef('pk')))
                ).only('account_id', 'is_active', 'is_suspended', 'credits').get(user=user)

                if vendor.has_refered:
                    messages.error(request, 'You have already referred a vendor. You cannot apply a referral code.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if page_path == '/vendor/billing/' and not vendor.is_active:
                    messages.error(request, 'Your account is not active. Please update your business details. To redeem apply code.')
                    return redirect('vendor:Details')

                if page_path == '/vendor/billing/' and vendor.is_suspended:
                    messages.error(request, 'Your account is suspended. Please contact support for more information.')
                    return redirect('vendor:Dashboard')
        
                if referral_code_to_account_id(_code) == vendor.account_id:
                    messages.error(request, 'You cannot apply your own referral code.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if vendor.has_referral_code:
                    messages.error(request, 'You have already applied this referral code.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if not referred_by.is_active:
                    messages.error(request, 'Referral code is not active.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                if referred_by.is_suspended:
                    messages.error(request, 'Referral code is suspended.')
                    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))

                AppliedReferral.objects.create(
                    vendor=vendor,
                    referred_by=referred_by,
                    code=_code,
                    info={'credits': 100}
                )                
                messages.success(request, f"<p class='mb-0'>Referral code applied successfully. You'll receive 100 credits after &nbsp;<strong>{referred_by.name}</strong>&nbsp; approves your referral.</p>")
                return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))
            
    messages.error(request, 'Invalid code.')
    return redirect(request.META.get('HTTP_REFERER', 'vendor:Billing'))


def create_rezorpay_payment(amount, payment_type):
    if amount <= 0:
        raise ValueError("Invalid amount")

    amount = int(amount * 100)
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Test the credentials with a simple request
    try:
        client.order.all()
    except razorpay.errors.BadRequestError as e:
        print("API Authentication failed!", e)
    
    # Create Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount, currency='INR', payment_capture='1'))

    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'order_id': razorpay_order['id'],
        'payment_type': payment_type
    }
    return context


def generate_transaction_id():
    return str(uuid.uuid4()).replace("-", "").upper()[:10]


def calculate_price(request, custom_datetime=None):
    # Check if price has already been calculated for the day. Check in track_billing table
    _date = date.today()
    days_in_month = calendar.monthrange(_date.year, _date.month)[1]
    if custom_datetime is not None:
        _date = custom_datetime

    today_exists_track_billing = TrackBilling.objects.filter(created_at__date=_date)
    today_exists_track_billing = set(TrackBilling.objects.filter(created_at__date=_date).values_list('vendor_id', flat=True))
    # if today_exists_track_billing is not None:
    #     # vendors = Vendor.objects.only('id', 'bill', 'auto_bill_settlement_credits', 'credits', 'email', 'name', 'user').filter(is_suspended=False, is_active=True)
    #     # for vendor in vendors:
    #     #     yesterday = today - timedelta(days=1)
    #     #     trackbill = TrackBilling.objects.get(vendor=vendor, created_at__date=yesterday)
    #     #     amount = trackbill.amount
    #     #     vendor.credits += amount
    #     #     vendor.save()

    #     #     # select the last Transaction created yesterday
    #     #     last_transaction = Transaction.objects.filter(user=vendor.user, transaction_type='debit', created_at__date=yesterday, description='Auto Bill settlement using credit.').order_by('-created_at').first()
    #     #     if last_transaction is not None:
    #     #         last_transaction.amount -= amount
    #     #         last_transaction.save()
    #     # messages.success(request, 'Bill revoked for yesterday.')
    #     # Return date in Short Month Date, Year format
    #     return messages.error(request, f'Bill already calculated for date {_date.strftime("%b %d, %Y")}.')
    
    # Fetch all necessary data in a single query
    vendors = Vendor.objects.select_related('user').filter(
        is_suspended=False, is_active=True, created_at__lte=_date
    ).only('active_services', 'active_features', 'id', 'bill', 'auto_bill_settlement_credits', 'credits', 'email', 'name', 'user')
    pricing_tags = Pricing.objects.all()
    
    # Convert pricing tags into a dictionary for quick access
    pricing_dict = {price.tag.lower(): price.price for price in pricing_tags}
    
    # Prepare lists for updates and transactions
    vendors_to_update = []
    transactions_to_create = []
    track_billing = []

    # Calculate bill for each vendor
    for vendor in vendors:
        
        # Check if vendor has a bill in today_exists_track_billing variable
        if vendor.id in today_exists_track_billing:
            continue
        
        total_price = 0
        active_services = vendor.active_services
        active_features = vendor.active_features

        if not active_services and not active_features:
            continue

        active_services_bill_track = {}
        active_features_bill_track = {}
        other_bill_track = {}
        total = {
            "active_services": 0,
            "active_features": 0,
            "other": 0
        }

        for service_tag, is_active in active_services.items():
            service_key = service_tag.split('-[')[0].lower()
            if is_active and service_key in pricing_dict:
                price = round(float(pricing_dict[service_key]), 2)
                total_price += price
                active_services_bill_track[service_key] = price
                total['active_services'] += price

        for feature_tag, is_active in active_features.items():
            feature_key = feature_tag.split('-[')[0].lower()
            if is_active and feature_key in pricing_dict:
                price = round(float(pricing_dict[feature_key]), 2)
                total_price += price
                active_features_bill_track[feature_key] = price
                total['active_features'] += price

        # Calculate platform fee
        if 'platform_fee' in pricing_dict:
            platform_fee_per_day = round(float(pricing_dict['platform_fee'] / days_in_month), 2)
            other_bill_track['platform_fee'] = platform_fee_per_day
            total_price += platform_fee_per_day
            total['other'] += platform_fee_per_day

        vendor.bill += Decimal(total_price)
        vendors_to_update.append(vendor)

        track_billing.append(
            TrackBilling(
                vendor_id=vendor.id,
                active_services=active_services_bill_track,
                active_features=active_features_bill_track,
                other=other_bill_track,
                amount=total_price,
                pricing=total,
                created_at=_date,
                updated_at=_date
            )
        )
    # Bulk update all vendors with their new bill amounts
    with transaction.atomic():
        Vendor.objects.bulk_update(vendors_to_update, ['bill'])
        TrackBilling.objects.bulk_create(track_billing)

    # Calculate dates
    today = _date
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Determine if today is the first or last day of the month
    is_last_day = today == last_day_of_month
    is_first_day = today == first_day_of_month
    # is_last_day = True

    if (is_last_day or is_first_day) and custom_datetime is None:
        # Filter vendors with bills greater than zero
        vendors_with_bills = Vendor.objects.filter(bill__gt=0)

        # Make the due date more redable format
        pay_by = (last_day_of_month + timedelta(days=5)).strftime("%b %d, %Y")
        due_date = today.strftime("%b %d, %Y")

        # Current year
        current_year = datetime.now().year

        # Prepare reminder emails and handle auto-bill settlement
        reminders = []

        for vendor in vendors_with_bills:
            if is_last_day and vendor.auto_bill_settlement_credits and vendor.credits > 0:
                # Deduct credit to settle the bill
                if vendor.bill > vendor.credits:
                    deducted_amount = vendor.credits
                    vendor.bill -= vendor.credits
                    vendor.credits = 0
                else:
                    deducted_amount = vendor.bill
                    vendor.credits -= vendor.bill
                    vendor.bill = 0
                
                # deducted_amount = min(vendor.bill, vendor.credits)
                # vendor.bill -= deducted_amount
                # vendor.credits -= deducted_amount

                # Create transaction for credit deduction
                transactions_to_create.append(
                    Transaction(
                        transaction_id=generate_transaction_id(),
                        user_id=vendor.user.id,
                        transaction_type='debit',
                        amount=deducted_amount,
                        method='point',
                        description='Auto Bill settlement using credit.'
                    )
                )
            if vendor.bill > 50:
                # Append reminders for vendors with remaining bills
                reminders.append({
                    'name': vendor.name,
                    'email': vendor.email,
                    'bill': vendor.bill,
                    'due_date': due_date,
                    'pay_by': pay_by,
                    'year': current_year
                })
                
                vendors_to_update.append(vendor)

        # Bulk save updated vendors and create transactions
        if is_last_day:
            with transaction.atomic():
                Vendor.objects.bulk_update(vendors_with_bills, ['bill', 'credits'])
                Transaction.objects.bulk_create(transactions_to_create)


        # Send reminders (email sending logic can be abstracted to a utility function)
        send_payment_reminder_email(reminders)

    return messages.success(request, "Bill has been updated successfully.")

