from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404

from authenticator.decorators import has_permission
from .models import Invitation as InvitationData, \
    Template as TemplateData, \
    RSVP as RSVPData, \
    Review, \
    ReportReview, \
    TemplateReport, \
    Save, \
    Like
from payment.models import Payment
from django.db.models import Count, Prefetch, Q , Avg
from datetime import date, timedelta, datetime
from django.contrib import messages
from .country_mapping import COUNTRIES
from .currency_mapping import calculate_price
import json
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.utils import send_email_with_backend
from .data import invitation_tags, trivias as trivias_data  # Import invitation_tags
from vendor.views import get_cached_user
from django.core.files.storage import default_storage





razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# Create your views here for cms

@login_required
def cms_invitation_dashboard(request, id):
    user = request.user
    invitation = InvitationData.objects.prefetch_related('template', 'rsvps').annotate(
        rsvps_count=Count('rsvps', distinct=True),
    ).get(id=id)

    # Calculate RSVP counts
    rsvp_yes_count = invitation.rsvps.filter(attending='yes').count()
    rsvp_no_count = invitation.rsvps.filter(attending='no').count()
    rsvp_maybe_count = invitation.rsvps.filter(attending='maybe').count()

    data = {
        'user': user,
        'cp': 'invitations',
        'invitation': invitation,
        'rsvp_yes_count': rsvp_yes_count,
        'rsvp_no_count': rsvp_no_count,
        'rsvp_maybe_count': rsvp_maybe_count,
    }
    return render(request, 'invitation/cms/pages/invitation.html', data)


def cms_invitation_rsvps(request, id):
    user = get_cached_user(request)
    invitation = InvitationData.objects.prefetch_related(
        Prefetch('rsvps', queryset=RSVPData.objects.order_by('-created_at')) #.order_by('-created_at')
    ).get(id=id)

    data = {
        'user': user,
        'cp': 'invitations',
        'invitation': invitation
    }
    return render(request, 'invitation/cms/pages/rsvps.html', data)


def home(request):
    user = get_cached_user(request)

    # Create base queryset
    templates = TemplateData.objects.filter(active=True)

    # Handle prefetch related differently for authenticated vs anonymous users
    if user.is_authenticated:
        templates = templates.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(status='approved')),
            Prefetch('template_likes', queryset=Like.objects.filter(user=user)),
            Prefetch('template_saves', queryset=Save.objects.filter(user=user)),
        )
    else:
        templates = templates.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(status='approved'))
        )

    # Annotate with review count and average rating
    templates = templates.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    )

    # Process templates
    for template in templates:
        if user.is_authenticated:
            template.is_liked = template.template_likes.filter(user=user).exists()
            template.is_saved = template.template_saves.filter(user=user).exists()
        else:
            template.is_liked = False
            template.is_saved = False

        # Use annotated values instead of recalculating
        template.avg_rating = template.avg_rating or 0

    data = {
        'templates': templates,
        'user': user,
    }
    return render(request, 'invitation/pages/home.html', data)


def template_information(request, id):
    user = get_cached_user(request)
    
    template = TemplateData.objects.prefetch_related(
        Prefetch('reviews', queryset=Review.objects.filter(status='approved')),
        Prefetch('template_likes', queryset=Like.objects.filter(user=user)),
        Prefetch('template_saves', queryset=Save.objects.filter(user=user)),
    ).annotate(review_count=Count('reviews')).get(id=id)

    avg_rating = template.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = template.reviews.count()
    has_purchased = False

    # Check if the user has liked or saved the template
    template.is_liked = template.template_likes.filter(user=user).exists()
    template.is_saved = template.template_saves.filter(user=user).exists()
    template.avg_rating = round(avg_rating, 1)
    template.review_count = review_count
    
    if request.user.is_authenticated:
        # Check if the user has purchased the template (is_paid=True)
        has_purchased = InvitationData.objects.filter(user=request.user, template=template, is_paid=True).exists()

    template.has_purchased = has_purchased

    data = {
        'user': user,
        'template': template,
    }
    return render(request, 'invitation/pages/template_information.html', data)


def template_preview(request, id):
    template = TemplateData.objects.get(id=id)
    template_path = template.path
    data = {
        'page': 'preview',
        'invitation': template
    }
    return render(request, f'invitation/{ template_path }/details.html', data)


def create_invitation(request, id):
    template_detail = TemplateData.objects.get(id=id)
    template_path = template_detail.path

    # Get the trivias_data accounding to the template type
    template_type = template_detail.invitation_type.lower()
    triviaOptions = trivias_data.get(template_type, [])
    
    today = date.today()
    default_start_date = today.strftime("%Y-%m-%d")

    data = {
        'page': 'create',
        'template': template_detail,
        'default_start_date': default_start_date,
        'countries': COUNTRIES,
        'triviaOptions': triviaOptions,
    }
    return render(request, f'invitation/{ template_path }/build.html', data)


def update_invitation(request, id):
    invitation = InvitationData.objects.prefetch_related('template').get(id=id)
    template_path = invitation.template.path

    today = date.today()
    default_start_date = today.strftime("%Y-%m-%d")
    # Change the date format for th invitation start and end date
    invitation.start_date = invitation.start_date.strftime("%Y-%m-%d")
    invitation.end_date = invitation.end_date.strftime("%Y-%m-%d")

    data = {
        'page': 'update',
        'template': invitation.template,
        'invitation': invitation,
        'default_start_date': default_start_date,
        'invitation_data': json.dumps(invitation.details),
        'countries': COUNTRIES
    }
    return render(request, f'invitation/{template_path}/build.html', data)


def wedding_rsvp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        invitation_id = data.get('invitation_id')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        team = data.get('team')
        attending = data.get('attending', 'yes')

        RSVPData.objects.create(invitation_id=invitation_id, name=name, email=email, phone=phone, attending=attending, message=message, team=team.lower())
        return JsonResponse({'message': 'Wedding RSVP submitted successfully.', 'success': True}, status=200)

    return JsonResponse({'error': 'Invalid request.', 'success': False}, status=400)


def delete_invitation(request, id):
    invitation = InvitationData.objects.get(id=id)
    if invitation.user != request.user:
        messages.error(request, "You don't have permission to delete this invitation.")
        return redirect('invitation:home')
    
    messages.success(request, "Invitation deleted successfully.")
    invitation.delete()
    return redirect('invitation:home')


def invitation_payment(request, invitation_type, template_id):
    return render(request, 'invitation/pages/payment.html')


@csrf_exempt # This is required to allow the Razorpay webhook to send POST requests
@login_required # This is required to ensure that only authenticated users can access this view
def generate_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        invitation_data = data.get("invitation_data", {})
        page = data.get("page", "")
        template_id = invitation_data.get("template", {}).get("id", "")
        invitation_id = data.get("invitation_id", "")
        
        # Calculate total price dynamically
        total_amount = 0
        invitation_info = TemplateData.objects.filter(id=template_id).values().first()
        invitationType = invitation_info.get("invitation_type", "")

        if not invitation_info:
            return JsonResponse({"error": "Invalid invitation type or template"}, status=400)

        invitation_price = invitation_info.get("price", 0)

        invitation_start_date = invitation_data.get("startDate", "")
        invitation_end_date = invitation_data.get("endDate", "")

        # Calculate the total amount based on the number of days
        new_start_date = datetime.strptime(invitation_start_date, "%Y-%m-%d")
        new_end_date = datetime.strptime(invitation_end_date, "%Y-%m-%d") 
        new_total_days = (new_end_date - new_start_date).days
        free_days = invitation_info.get("free_days", 0)

        rsvp_enabled = invitation_data.get("invitation", {}).get("rsvp", False)
        comments_enabled = invitation_data.get("invitation", {}).get("comment", False)
        thankYouPage_enabled = invitation_data.get("invitation", {}).get("thankYouPage", False)
        
        rsvp_price = invitation_price * 0.1 if rsvp_enabled else 0 # 25% of the invitation price
        comment_price = invitation_price * 0.1 if comments_enabled else 0 # 25% of the invitation price

        new_thankYouPage_days = invitation_data.get("invitation", {}).get("thankYouPageDays", 0) if thankYouPage_enabled else 0

        old_total_days = 0
        utilized_total_days = 0
        remaining_old_days = 0

        if page == 'update':
            _invitation = InvitationData.objects.get(id=invitation_id, user=request.user)
            if _invitation:
                old_start_date = _invitation.start_date
                old_end_date = _invitation.end_date
                # Chnage date format
                old_start_date = datetime.strptime(str(old_start_date), "%Y-%m-%d")
                old_end_date = datetime.strptime(str(old_end_date), "%Y-%m-%d")
                old_total_days = (old_end_date - old_start_date).days

                # Check how many days has been utilized from the old invitation
                if _invitation.end_date < datetime.now().date():
                    # If the old invitation is expired, set the old total days to 0
                    utilized_total_days = 0
                else:
                    # Calculate the number of days already utilized from the old invitation
                    utilized_total_days = (datetime.now().date() - _invitation.start_date).days
                
                remaining_old_days = old_total_days - utilized_total_days # The remaining days from the old invitation

                # Check for Thank You Page days
                old_thankYouPage_days = _invitation.details.get('thankYouPageDays', 0)
                if int(old_thankYouPage_days) < int(new_thankYouPage_days):
                    # If the new Thank You Page days are greater than the old ones, add the difference to the total days
                    new_thankYouPage_days = int(new_thankYouPage_days) - int(old_thankYouPage_days)
                else:
                    # If the old Thank You Page days are greater than the new ones, set it to 0
                    new_thankYouPage_days = 0

        if page == 'create' and thankYouPage_enabled:
            thankYouPage_price = (invitation_price * 0.25) * (int(new_thankYouPage_days) - 2)
        elif page == 'update' and thankYouPage_enabled:
            thankYouPage_price = (invitation_price * 0.25) * int(new_thankYouPage_days)
        else:
            thankYouPage_price = 0

        total_days = new_total_days - remaining_old_days # The total number of days for which the service will be provided
        total_days = total_days if total_days > 0 else 0
        invoice_days = (total_days - free_days) if total_days > free_days and page == 'create' else total_days # The number of days for which the invoice will be generated

        if invoice_days > 0:
            template_total_amount = invitation_price * total_days # The total amount for the template
            template_invoice_amount = invitation_price * invoice_days
            rsvp_amount = rsvp_price * invoice_days # The invoice amount for RSVP
            comment_amount = comment_price * invoice_days # The invoice amount for comments
            invoice_amount = template_invoice_amount + rsvp_amount + comment_amount
            total_amount = total_days * (invitation_price + rsvp_price + comment_price)
        else:
            template_total_amount = 0
            template_invoice_amount = 0
            invoice_amount = 0
            rsvp_amount = 0
            comment_amount = 0

        invoice_amount = invoice_amount + thankYouPage_price # The total amount for the invoice
        total_amount = total_amount + thankYouPage_price # The total amount for the service

        data = {}

        invoice_data = {
            "invoice_amount": invoice_amount,
            "template_total_amount": template_total_amount,
            "template_offer_amount": template_total_amount - template_invoice_amount,
            "total_days": total_days,
            "free_days": free_days,
            "start_date": invitation_start_date,
            "end_date": invitation_end_date,
            "invitationType": invitationType,
            "rsvp_amount": rsvp_amount,
            "comment_amount": comment_amount,
            "thank_you_page_amount": thankYouPage_price,
            "thank_you_page_days": new_thankYouPage_days,
            "total_amount": total_amount,
            "page": page,
        }
        
        if invoice_amount != 0:
            country_code = invitation_data.get('invitation', {}).get("venueLocation", {}).get("countryCode", "DEFAULT")
            _invoice_amount = calculate_price(invoice_amount, country_code)
            _template_total_amount = calculate_price(template_total_amount, country_code)
            _template_offer_amount = calculate_price(invoice_data['template_offer_amount'], country_code)
            _rsvp_amount = calculate_price(rsvp_amount, country_code)
            _comment_amount = calculate_price(comment_amount, country_code)
            _thank_you_page_amount = calculate_price(thankYouPage_price, country_code)
            _total_amount = calculate_price(total_amount, country_code)

            invoice_data['invoice_amount'] = _invoice_amount['converted_price'] / 100
            invoice_data['template_total_amount'] = _template_total_amount['converted_price'] / 100
            invoice_data['template_offer_amount'] = _template_offer_amount['converted_price'] / 100
            invoice_data['rsvp_amount'] = _rsvp_amount['converted_price'] / 100
            invoice_data['comment_amount'] = _comment_amount['converted_price'] / 100
            invoice_data['thank_you_page_amount'] = _thank_you_page_amount['converted_price'] / 100
            invoice_data['total_amount'] = _total_amount['converted_price'] / 100

            # Create Razorpay Order
            order_data = {
                "amount": int(_invoice_amount['converted_price']),  # Razorpay accepts amounts in paise
                "currency": _invoice_amount['currency'],
                "payment_capture": "1",
            }
            order = razorpay_client.order.create(order_data)

            data["order_id"] = order["id"]
            data["currency"] = order["currency"]
            data["amount"] = order['amount']
            data["razorpay_key_id"] = settings.RAZORPAY_KEY_ID
            data['description'] = f"Payment for {invitationType} invitation {invitation_info['name']} for {total_days} days"
            data['is_payment_required'] = True

            invoice_data['currency'] = order['currency']
            invoice_data['symbol'] = _invoice_amount['symbol']
            invoice_data['is_payment_required'] = True
        else:
            data['is_payment_required'] = False
            invoice_data['is_payment_required'] = False
            data['amount'] = 0

        data["html"] = render(request, "invitation/pages/payment_invoice.html", invoice_data).content.decode("utf-8")
        return JsonResponse(data)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def payment_success(request):
    if request.method == "POST" and 'razorpay_payment_id' in request.POST:
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        data = request.POST.get('data', "{}")
        amount = request.POST.get('amount', '0')
        amount = int(amount) / 100 if int(amount) else 0
        description = request.POST.get('description', "Payment for invitation")

        if not request.user.is_authenticated:
            return redirect('auth:auth_redirect_view')
        
        user_id = request.user.id

        # Save order details in the database
        payment = Payment(
            order_id=order_id,
            status='CREATED',
            payment_id=payment_id, 
            amount=amount
        )
        payment.user_id = user_id
        payment.save()

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(params_dict)
            payment.status = 'SUCCESS'
            payment.save(description=description)

        except Exception as e:
            payment.status = 'FAILED'
            payment.save(description=description)
            return render(request, "invitation/pages/payment_failed.html")
        
        # Create the invitation
        invitation_data = json.loads(data)
        template_id = invitation_data.get("template", {}).get("id", "")
        template = TemplateData.objects.get(id=template_id) if template_id else None
        start_date = invitation_data.get("startDate", "")
        end_date = invitation_data.get("endDate", "")
        details = invitation_data.get('invitation', {})
        invitation = InvitationData.objects.create(
            user_id=user_id,
            template_id=template_id,
            details=details,
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            is_paid=True,
        )
        invitation.save()
        settings.THREAD_POOL_EXECUTOR.submit(
            send_email_with_backend,
            subject='Invitation Created Successfully',
            template_name='invitation/emails/payment_success.html',
            email_info={
                'from': "Eventic <notification@eventic.in>",
                'to': [request.user.email],
            },
            context={
                'invitation': invitation,
                'template': template
            },
            backend_name="default"
        )
        return render(request, "invitation/pages/payment_success.html", {"invitation_id": invitation.id})
    
    if request.method == "POST" and 'publish_data' in request.POST:
        data = json.loads(request.POST.get('publish_data', "{}"))
        amount = request.POST.get('amount', 0)
        template_id = data.get("template", {}).get("id", "")
        start_date = data.get("startDate", "")
        end_date = data.get("endDate", "")
        details = data.get('invitation', {})
        
        if int(amount) != 0:
            return JsonResponse({'error': 'Invalid request.'}, status=400)
        
        template = TemplateData.objects.get(id=template_id) if template_id else None
        
        invitation = InvitationData.objects.create(
            user=request.user,
            template_id=template_id,
            details=details,
            start_date=start_date,
            end_date=end_date,
            amount=0,
            is_paid=False,
        )
        invitation.save()
        settings.THREAD_POOL_EXECUTOR.submit(
            send_email_with_backend,
            subject='Invitation Created Successfully',
            template_name='invitation/emails/payment_success.html',
            email_info={
                'from': "Eventic <notification@eventic.in>",
                'to': [request.user.email],
            },
            context={
                'invitation': invitation,
                'template':template
            },
            backend_name="default"
        )
        return render(request, "invitation/pages/payment_success.html", {"invitation_id": invitation.id})
    
    return render(request, "invitation/pages/payment_failed.html")


@login_required
def toggle_pin_unpin_review(request, review_id, template_id):
    if request.method == 'POST' and 'pinUnpin' in request.POST:
        review = get_object_or_404(Review, id=review_id)
        review.pinned = False if review.pinned else True
        review.save()

        action = "pinned" if review.pinned else "unpinned"
        messages.success(request, f"Review {action} successfully.")
        return redirect('invitation:template_information', id=template_id)

    return JsonResponse({"error": "You do not have permission to pin this review."}, status=403)


@login_required
def add_review(request, template_id):
    # Check if the user has purchased the template (is_paid=True)
    if request.method == "POST":
        invitation_info = InvitationData.objects.prefetch_related('template').filter(user=request.user, template_id=template_id, is_paid=True)
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not invitation_info.exists():
            return JsonResponse({"error": "You need to purchase the template to add a review."}, status=403)
        
        _invitation = invitation_info.first()

        _data = {}
        if _invitation.template.invitation_type == "wedding":
            _data = {
                'template_type': (_invitation.template.invitation_type).lower(),
                'groom': _invitation.details.get('groom', ''),
                'bride':_invitation.details.get('bride', ''),
                'date': _invitation.details.get("eventDate", ''),
                'venue': _invitation.details.get("venueLocation", {}).get("venue", ''),
                'city': _invitation.details.get("venueLocation", {}).get("city", ''),
                'state': _invitation.details.get("venueLocation", {}).get("state", ''),
                'country': _invitation.details.get("venueLocation", {}).get("countryName", ''),
                'zip': _invitation.details.get("venueLocation", {}).get("zip", ''),
            }
        Review.objects.create(
            user=request.user,
            template_id=template_id,
            rating=rating,
            comment=comment,
            other=_data
        )
        messages.success(request, "Your review has been added successfully.")
        return redirect("invitation:template_information", id=template_id)

    messages.error(request, "Invalid request method.")
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect("invitation:template_information", id=review.template.id)

@login_required
def edit_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id, user=request.user)
        review.rating = request.POST.get("rating")
        review.comment = request.POST.get("comment")
        review.save()
        messages.success(request, "Review updated successfully.")
        return redirect("invitation:template_information", id=review.template.id)
    return redirect("invitation:template_information", id=review.template.id)

@login_required
def report_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        reason = request.POST.get("reason")

        ReportReview.objects.create(
            review=review,
            user=request.user,
            reason=reason,
        )
        messages.success(request, "Review reported successfully.")
        return redirect("invitation:template_information", id=review.template.id)
    messages.error(request, "Invalid request method.")
    return redirect("invitation:template_information", id=review.template.id)

@login_required
def report_template(request, template_id):
    if request.method == "POST":
        template = get_object_or_404(TemplateData, id=template_id)
        reason = request.POST.get("reason")
        description = request.POST.get("description")
        screenshot = request.FILES.get("screenshot")  # Handle uploaded screenshot

        TemplateReport.objects.create(
            template=template,
            user=request.user,
            reason=reason,
            description=description,
            screenshot=screenshot,  # Save the screenshot
        )
        messages.success(request, "Template reported successfully.")
        return redirect("invitation:template_information", id=template_id)
    messages.error(request, "Invalid request method.")
    return redirect("invitation:template_information", id=template_id)

def delete_expired_invitations():
    # This function can be called periodically (e.g., via a cron job) to delete expired invitations
    from django.utils import timezone
    expired_invitations = InvitationData.objects.filter(end_date__lt=timezone.now().date())
    expired_invitations.delete()



@has_permission('admin')
def add_template(request):
    if request.method == "POST" and 'create' in request.POST:
        template_id = request.POST.get("template_id")
        name = request.POST.get("name")
        description = request.POST.get("description")
        thumbnail = request.FILES.get("thumbnail", None)
        invitation_type = request.POST.get("invitation_type")
        price = request.POST.get("price")
        free_days = request.POST.get("free_days")
        path = request.POST.get("path")
        tags = request.POST.getlist("tags")  # Get selected tags as a list
        tags_str = ",".join(tags) 
        template_invite_card = request.FILES.get("template_invite_card")  # Get the template_invite_card
        
        if thumbnail is not None:
            thumbnail.name = f"{uuid4()}.{thumbnail.name.split('.')[-1]}"
            thumbnail_path = default_storage.save(f'templates/{thumbnail.name}', thumbnail)
            thumbnail = default_storage.url(thumbnail_path)
        else:
            thumbnail = None
            
        if template_invite_card is not None:
            template_invite_card.name = f"{uuid4()}.{template_invite_card.name.split('.')[-1]}"
            invite_card_path = default_storage.save(f'templates/{template_invite_card.name}', template_invite_card)
            template_invite_card = default_storage.url(invite_card_path)
        else:
            template_invite_card = None
        
        path = f"{invitation_type}/{path}"
        Template_info ={
            'invite_card': template_invite_card, 
        } 

        TemplateData.objects.create(
            template_id=template_id,
            user=request.user,
            name=name,
            description=description,
            thumbnail=thumbnail,
            invitation_type=invitation_type,
            price=price,
            free_days=free_days,
            path=path,
            tag=tags_str,
            info=Template_info
        )
        messages.success(request, "Template added successfully.")
        return redirect("dashboard:Templates")
    data ={
        'cp': 'create',
        'invitation_tags': invitation_tags,
        'TYPES': TemplateData.TYPES  # Pass the TYPES field to the template
    }
    return render(request, "invitation/cms/pages/edit_template.html", data)

def edit_template(request, template_id=None):
    template = None
    
    if template_id:
        template = get_object_or_404(TemplateData, id=template_id)  # Fetch the template to pre-fill the form
        
    if request.method == "POST" and 'update' in request.POST:
        tags = request.POST.getlist("tags")  # Get selected tags as a list
        tags_str = ",".join(tags)  # Convert the list to a comma-separated string
        if template:
            template.template_id = request.POST.get("template_id")
            template.invitation_type = request.POST.get("invitation_type")
            template.name = request.POST.get("name")
            template.description = request.POST.get("description")  # Save rich text content
            template.price = request.POST.get("price")
            template.free_days = request.POST.get("free_days")
            template.tag = tags_str  # Save tags as a comma-separated string
            if "thumbnail" in request.FILES:
                thumbnail = request.FILES.get("thumbnail")
                if not template.thumbnail or thumbnail.name != template.thumbnail.split('/')[-1]:
                    if template.thumbnail:
                        default_storage.delete(template.thumbnail.replace('/media/', ''))
                    thumbnail.name = f"{uuid4()}.{thumbnail.name.split('.')[-1]}"
                    thumbnail_path = default_storage.save(f'templates/{thumbnail.name}', thumbnail)
                    template.thumbnail = default_storage.url(thumbnail_path)
            
            if "template_invite_card" in request.FILES:
                template_invite_card = request.FILES.get("template_invite_card")
                if not template.info.get('invite_card') or template_invite_card.name != template.info['invite_card'].split('/')[-1]:
                    if template.info.get('invite_card'):
                        default_storage.delete(template.info['invite_card'].replace('/media/', ''))
                    template_invite_card.name = f"{uuid4()}.{template_invite_card.name.split('.')[-1]}"
                    invite_card_path = default_storage.save(f'templates/{template_invite_card.name}', template_invite_card)
                    template.info['invite_card'] = default_storage.url(invite_card_path)
            
            template.save()
            messages.success(request, f"Template '{template.name}' updated successfully.")
            
        return redirect("invitation:home")

    data = {
        'cp': 'edit',
        'invitation_tags': invitation_tags,
        'template': template,
        'TYPES': TemplateData.TYPES  # Pass the TYPES field to the template
    }
    return render(request, "invitation/cms/pages/edit_template.html", data)


@login_required
def toggle_like_template(request, template_id):
    template = get_object_or_404(TemplateData, id=template_id)
    like_instance = Like.objects.filter(user=request.user, template=template).first()

    if like_instance:
        like_instance.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, template=template)
        liked = True

    return JsonResponse({"liked": liked})


@login_required
def toggle_save_template(request, template_id):
    template = get_object_or_404(TemplateData, id=template_id)
    save_instance = Save.objects.filter(user=request.user, template=template).first()

    if save_instance:
        save_instance.delete()
        saved = False
    else:
        Save.objects.create(user=request.user, template=template)
        saved = True

    return JsonResponse({"saved": saved})


