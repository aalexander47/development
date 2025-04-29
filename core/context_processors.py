# core/context_processors.py

from django.conf import settings

def global_settings(request):
    """
    Add custom settings to the context to make them available in templates.
    """
    return {
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'GOOGLE_ANALYTICS': settings.GOOGLE_ANALYTICS,
        'GOOGLE_OAUTH': settings.GOOGLE_OAUTH,
        'IN_DEVELOPMENT': settings.IN_DEVELOPMENT,
        'HIDDEN': False,
        'DEBUG': settings.DEBUG,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'CONTACT_PHONE': settings.CONTACT_PHONE,
        'INSTAGRAM': settings.INSTAGRAM,
        'FACEBOOK': settings.FACEBOOK,
        'TWITTER': settings.TWITTER,
        'YOUTUBE': settings.YOUTUBE,
        'LINKEDIN': settings.LINKEDIN,
        'WHATSAPP': settings.WHATSAPP
    }