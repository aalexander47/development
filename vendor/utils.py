from PIL import Image
from django.core.cache import cache
from .models import Vendor


# create a function to detect image and categories it as landscape or portrait or square
def detect_image_category(image):
    img = Image.open(image)
    width, height = img.size
    if width == height:
        return "square"
    elif width > height:
        return "landscape"
    else:
        return "portrait"
    
def get_cached_vendor(request):
    vendor = cache.get(f'cached_vendor_{request.user.id}')
    if not vendor:
        vendor = Vendor.objects.get(user=request.user)
        cache.set(f'cached_vendor_{request.user.id}', vendor, 60 * 60 * 24)  # Cache for 24 hours
    return vendor


def account_id_to_referral_code(account_id):
    """
    Convert an account ID to a referral code by rearranging characters
    and inserting 'R', 'F', 'C' after every two characters.

    Args:
        account_id (str): The original account ID.

    Returns:
        str: The generated referral code.
    """
    # Define the fixed positions for rearranging
    positions = [1, 7, 3, 5, 2, 4, 0, 6]  # Example positions
    # Characters to insert after every two characters
    add_chars = ['R', 'F', 'C']
    
    # Check if the account_id length matches the positions
    if len(account_id) != len(positions):
        raise ValueError("The account_id length must match the predefined positions.")
    
    # Rearrange the account_id based on positions
    rearranged = ''.join(account_id[i] for i in positions)
    
    # Insert characters after every two characters
    final_code = []
    add_index = 0  # To track which character from add_chars to add
    for i, char in enumerate(rearranged):
        final_code.append(char)
        # Add characters from add_chars after every 2 characters
        if (i + 1) % 2 == 0 and add_index < len(add_chars):
            final_code.append(add_chars[add_index])
            add_index += 1
    
    return ''.join(final_code)

def referral_code_to_account_id(referral_code):
    """
    Convert a referral code back to the original account ID
    by removing inserted characters at specific positions
    and restoring the original order.

    Args:
        referral_code (str): The referral code to reverse.

    Returns:
        str: The original account ID.
    """
    # Check if R, F, and C are inserted at specific positions
    referral_code = list(referral_code)
    if referral_code[2] != 'R' or referral_code[5] != 'F' or referral_code[8] != 'C' or len(referral_code) == 11:
        return ""
    
    print(referral_code, '\nlength: ', len(referral_code))

    # Define the fixed positions for rearranging
    positions = [1, 7, 3, 5, 2, 4, 0, 6]  # Used in the original process
    
    # Remove inserted characters ('R', 'F', 'C') at their specific positions
    # R is after the 2nd char, F is after the 4th, C is after the 6th
    extracted_code = []
    for i, char in enumerate(referral_code):
        # Skip indices where R, F, and C are inserted
        if i not in {2, 5, 8}:  # Adjust based on the exact insertion logic
            extracted_code.append(char)

    # Rearrange the characters back to their original positions
    filtered_code = ''.join(extracted_code)
    original_code = [''] * len(positions)
    for i, pos in enumerate(positions):
        original_code[pos] = filtered_code[i]

    return ''.join(original_code)
