from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import get_connection
from core.utils import send_email_with_backend
from datetime import datetime
# from celery import shared_task

# @shared_task
def send_payment_reminder_email(reminders):
    for reminder in reminders:
        subject = "Payment Reminder"
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_year = datetime.now().year
        context = {
            'name': reminder.get('name'),
            'amount': reminder.get('bill'),
            'date': current_date,
            'year': current_year
        }
        send_email_with_backend(
            subject=subject,
            template_name="payment/emails/reminder.html",
            context=context,
            email_info={
                'from': "Payment Reminder Eventic <notification@eventic.in>",
                'to': [reminder.get('email')]
            },
            backend_name="info"
        )