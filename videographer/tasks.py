from core.utils import send_email_with_backend
# from celery import shared_task

# @shared_task
def send_callback_lead_email(email_to, vendor_name, client_name, cc_emails=[], bcc_emails=[]):
    subject = f"Callback Request From {client_name.title()}! Don't Miss Out!" if client_name else "You've Got a Callback Request! Don't Miss Out!"
    context = {'user_name': vendor_name, 'client_name': client_name}

    send_email_with_backend(
        subject=subject,
        template_name="videographer/email/callback.html",
        context=context,
        email_info={
            'from': "Eventic Leads <notification@eventic.in>",
            'to': [email_to],
            'cc': cc_emails,
            'bcc': bcc_emails
        },
        backend_name="info"
    )