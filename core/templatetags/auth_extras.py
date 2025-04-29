from django import template
from django.contrib.auth.models import Group
from datetime import date, datetime
from django.utils.timesince import timesince
import re

register = template.Library()

@register.filter
def round(value):
    return int(value) if value % 1 == 0 else round(value, 2)

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    return group in user.groups.all()

@register.filter(name='date_strftime')
def date_strftime(value, format):
    _date = datetime.strptime(value, "%Y-%m-%d")
    return _date.strftime(format)

@register.filter
def to_12_hour_format(time_24):
    try:
        hours, minutes = map(int, time_24.split(':'))
        period = 'PM' if hours >= 12 else 'AM'
        hours_12 = hours % 12
        if hours_12 == 0:
            hours_12 = 12
        return f"{hours_12}:{minutes:02d} {period}"
    except (ValueError, AttributeError):
        return "Invalid time format. Expected 'HH:MM'."

@register.filter(name='experience')
def experience(value):
    """Calculates years and months of experience based on a date string.

    Args:
        value: The date string in "Month. Day, Year" format (e.g., "Jan. 1, 2024").

    Returns:
        A string representing years and months of experience (e.g., "1 year, 3 months").
    """
    if not value:
        return ""
    try:
        # Parse the date string
        start_date = datetime.strptime(str(value), "%Y-%m-%d").date()
        today = date.today()

        # Calculate years and months
        years = today.year - start_date.year
        months = today.month - start_date.month

        # Handle negative months (rollover to previous year)
        if months < 0:
            years -= 1
            months += 12

        # Format the experience string
        experience_str = ""
        if years > 0:
            experience_str += f"{years} year{'s' if years > 1 else ''}"
        if years > 0 and months > 0:
            experience_str += ", "
        if months > 0:
            experience_str += f"{months} month{'s' if months > 1 else ''}"

        return experience_str
    except ValueError:
        return "Invalid date format"

@register.filter
def nl2br(value):
    return value.replace('\n', '<br>')

@register.filter(name='chucks')
def chunks(data, size):
    """Splits a list into nearly equal chunks.

    Args:
        data: The list to be chunked.
        size: The desired size of each chunk.

    Returns:
        A list of lists, where each sub-list is a chunk of the original data.
    """
    chunks = []
    average = len(data) // size  # Floor division for whole chunks

    for i in range(0, len(data), size):
        # Handle last chunk potentially being smaller
        end_index = min(i + size, len(data))
        chunks.append(data[i:end_index])

    # Distribute remaining elements if list length isn't divisible by size
    last_chunk = chunks.pop()
    for i in range(len(data) % size):
        last_chunk.append(data[average * size + i])
    chunks.append(last_chunk)

    return chunks

@register.filter
def timesince_simple(value, arg=None):
    # Use Django's built-in timesince filter to get the string.
    timesince_str = timesince(value, arg)
    
    # Split the timesince string to get individual components.
    parts = timesince_str.split(", ")
    
    # Return only the first part (e.g., "1 hour" or "23 minutes").
    return parts[0]

@register.filter
def startswith(value, arg):
    """Check if a string starts with the given arg."""
    return value.startswith(arg)

@register.filter
def endswith(value, arg):
    """Check if a string ends with the given arg."""
    return value.endswith(arg)


@register.filter(name='getdate')
def get_date_component(date_str, component):
    """
    Extract date components from various date string formats.
    
    Usage in template:
    {{ date_string|getdate:"d" }} -> Day (27)
    {{ date_string|getdate:"m" }} -> Month (12)
    {{ date_string|getdate:"Y" }} -> Year (2024)
    {{ date_string|getdate:"A" }} -> Weekday name (Friday)
    {{ date_string|getdate:"F" }} -> Month name (December)
    """
    if not date_str:
        return ""
    
    # Try to parse common date formats
    date_formats = [
        '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', 
        '%d.%m.%Y', '%b %d, %Y', '%d %B %Y',
        '%Y/%m/%d', '%m-%d-%Y', '%d %b %Y'
    ]
    
    date_obj = None
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(str(date_str), fmt)
            break
        except (ValueError, TypeError):
            continue
    
    if not date_obj:
        # Try to extract date from string using regex as fallback
        match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})', str(date_str))
        if match:
            day, month, year = match.groups()
            year = int(year)
            if year < 100:
                year += 2000 if year < 50 else 1900
            try:
                date_obj = datetime(year, int(month), int(day))
            except ValueError:
                pass
    
    if not date_obj:
        return "Invalid Date"
    
    # Return requested component
    component_map = {
        'd': date_obj.strftime('%d'),  # Day (01-31)
        'j': date_obj.strftime('%-d'),  # Day (1-31) - no leading zero
        'm': date_obj.strftime('%m'),  # Month (01-12)
        'n': date_obj.strftime('%-m'),  # Month (1-12) - no leading zero
        'Y': date_obj.strftime('%Y'),  # Year (2024)
        'y': date_obj.strftime('%y'),  # Year (24)
        'A': date_obj.strftime('%A'),  # Weekday name (Friday)
        'a': date_obj.strftime('%a'),  # Weekday abbrev (Fri)
        'F': date_obj.strftime('%B'),  # Month name (December)
        'M': date_obj.strftime('%b'),  # Month abbrev (Dec)
        'S': date_obj.strftime('%d') + {1: 'st', 2: 'nd', 3: 'rd'}.get(int(date_obj.strftime('%d')) % 20, 'th'),  # 27th
        'U': str(int(date_obj.timestamp())),  # Unix timestamp
    }
    
    return component_map.get(component, "Invalid Component")