from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import get_connection
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
# from celery import shared_task


# @shared_task
def send_email_with_backend(subject, template_name, context, email_info, backend_name='default'):
    backend_config = settings.EMAIL_BACKENDS.get(backend_name)
    if not backend_config:
        raise ValueError(f"No email backend configuration found with the name '{backend_name}'")

    # Load email template and prepare content
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    # Establish a connection using the specified backend settings
    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        **backend_config
    )

    # Create and send the email
    email = EmailMultiAlternatives(
        subject, 
        text_content, 
        email_info['from'], 
        email_info['to'],
        cc=email_info.get('cc', []),
        bcc=email_info.get('bcc', []),
        connection=connection
    )
    email.attach_alternative(html_content, "text/html")
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Error sending email with {backend_name}: {e}")
        

def soundex(word):
    """Returns the soundex representation of the given word."""
    if not word:
        return ""
    
    # Soundex conversion table
    soundex_table = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6'
    }
    
    # Convert to uppercase
    word = word.upper()
    
    # Save the first letter
    first_letter = word[0]
    
    # Convert rest of the letters
    encoded = first_letter + "".join(soundex_table.get(char, '') for char in word[1:])
    
    # Remove duplicate consecutive numbers
    encoded = encoded[0] + "".join(
        encoded[i] for i in range(1, len(encoded)) if encoded[i] != encoded[i - 1]
    )
    
    # Remove all zeros
    encoded = encoded.replace('0', '')
    
    # Pad or truncate to ensure it has four characters
    return (encoded + "000")[:4]


def compress_image(uploaded_image, quality=85):
    """
    Compress an uploaded image to reduce file size without significant quality loss.

    Args:
        uploaded_image (UploadedFile): The original image file uploaded by the user.
        quality (int): Compression quality (1-100). Lower values mean higher compression.

    Returns:
        Compressed image ready for saving to the database.
    """
    # Open the uploaded image
    img = Image.open(uploaded_image)
    img_format = img.format  # Preserve original format (e.g., JPEG, PNG)

    # Convert to RGB if the image is in a mode that doesn't support compression
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Compress the image and save it into an in-memory file
    buffer = BytesIO()
    img.save(buffer, format=img_format, optimize=True, quality=quality)
    buffer.seek(0)

    # Return the compressed image as a ContentFile (Django-friendly format)
    return ContentFile(buffer.read(), name=uploaded_image.name)