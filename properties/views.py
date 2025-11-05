from django.shortcuts import render

from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .utils import get_all_properties


@cache_page(60 * 15)  # Cache view response for 15 minutes
def property_list(request):
    """
    View to return all properties.
    Uses low-level cache API to cache queryset for 1 hour.
    View response is also cached for 15 minutes.
    """
    response = get_all_properties()

    # Extract properties list from the response
    properties = response.get('data', [])

    return JsonResponse({
        'count': len(properties),
        'data': properties
    }, safe=False)