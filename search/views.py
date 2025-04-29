from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F, Value, CharField, Prefetch, Exists, OuterRef, Subquery
from django.db.models.functions import Concat
from django.core.cache import cache
from django.core.files.storage import default_storage
from vendor.views import get_cached_user
from vendor.models import Vendor, Service, Gallery
import random, re



def vendor_search(request):
    user = get_cached_user(request)
    query = request.GET.get('q', '')
    service = request.GET.get('service', '')
    category = request.GET.get('category', '')

    if service == 'vendor' and category:
        return redirect(f'/{category}/search/?q={query}')
    elif service and service != 'vendor':
        return redirect(f'/{service}/search/{category}/?q={query}') if category else redirect(f'/{service}/search/?q={query}')

    results = search_with_ranking(query)

    data = {
        'query': query,
        'results': results,
        'user': user
    }
    return render(request, "search/pages/vendors.html", data) 

def search_with_ranking(search_string):
    """
    Searches for individual words in a search string, ranks results, and filters based on a match threshold.

    Args:
        search_string: The string containing words to search for.

    Returns:
        A list of dictionaries containing matched models and their word match counts.
    """
    stopwords = [
        "i", "me", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs", "what", "which", "that", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "been", "has", "have", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "or", "for", "nor", "so", "yet", "because", "near",
        "at", "by", "in", "into", "of", "on", "to", "with", "around",
        "as", "has", "have", "had", "having", "be", "s", "t", "can", "must", "will", "may", "might", "shall", "should", "would",
        "not", "no",
        "up", "down", "left", "right", "all", "any", "both", "each", "few", "more", "most", "some", "such", "other", "another",
        "very", "most", "only", "just", "too", "well", "also", "still", "even", "always",
    ]
    
    special_characters = ["#", "$", "%", "&","?", ".", ",", "!", ":", ";", '"', "'", "`", "-", "=", "+", "*", "/","|", "^", "(", ")", "[", "]", "{", "}"]

    search_ingnored = stopwords + special_characters

    conditions = Q(is_active=True)

    if search_string:
        words = search_string.lower().split()  # Split search string into lowercase words

        for word in words:
            if word not in search_ingnored:
                conditions &= Q(name__icontains=word) \
                                        | Q(address__icontains=word) \
                                        | Q(city__icontains=word) \
                                        | Q(state__icontains=word) \
                                        | Q(pincode__icontains=word) \
                                        | Q(bio__icontains=word) \
                                        | Q(active_services__icontains=word)

    results = (
        Vendor.objects.prefetch_related(
            Prefetch('services'),
        )
        .only('profile_picture', 'name', 'address', 'city', 'state', 'pincode', 'is_verified')
        .filter(conditions)
    )

    _search_results = []

    for result in results:
        if result.profile_picture and default_storage.exists(result.profile_picture.name):
            result.has_profile_picture = True

        _active_services = []

        for service in result.services.all():
            _active_service = {
                'service': service.content_object,
                'object': service
            }
            _active_services.append(_active_service)

        result.active_services = _active_services

        # choose_service = random.randint(0, len(_active_services) - 1)
        # service = _active_services[choose_service].get('service') 
        slug = (result.name).lower().replace(" ", "-")
        # Remove all the special characters except hyphens
        slug = re.sub(r'[^\w-]', '', slug)
        result.slug = slug

        if len(_active_services) > 0:
            _search_results.append(result)

    # Randmize the order of results
    random.shuffle(_search_results)

    return _search_results

