from allauth.account.forms import ResetPasswordForm
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

class CustomResetPasswordForm(ResetPasswordForm):
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        # Load the custom HTML template
        html_email_template_name = "account/email/password_reset_key_message.html"
        
        # Render the HTML email content
        html_content = render_to_string(html_email_template_name, context)
        
        # Create the email
        email = EmailMessage(
            subject=f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX} Password Reset",
            body=html_content,
            from_email=from_email,
            to=[to_email],
        )
        email.content_subtype = "html"  # Set content type to HTML
        email.send()
