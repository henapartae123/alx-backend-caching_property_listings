import logging
import uuid

from django.core.cache import cache
from django_redis import get_redis_connection

from .models import Property

logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Fetch all properties from cache or database.
    Caches the queryset in Redis for 1 hour (3600 seconds).

    Returns:
        QuerySet: All Property objects
    """
    # Try to get cached data
    cached_properties = cache.get('all_properties')

    if cached_properties is not None:
        print("Returning cached properties")
        return cached_properties

    # If not in cache, fetch from database
    print("Fetching properties from database")
    properties = Property.objects.all()

    # Convert to list to make it serializable for Redis
    properties_list = list(properties.values(
        'property_id', 'title', 'description', 'price', 'location', 'created_at'
    ))

    # Add sample data if no properties exist and store to database
    if not properties_list:
        print("No properties found in database. Adding sample data.")
        sample_properties = [
            {
                'property_id': str(uuid.uuid4()),
                'title': 'Sample Property 1',
                'description': 'A beautiful sample property.',
                'price': 100.00,
                'location': 'Sample Location 1'
            },
            {
                'property_id': str(uuid.uuid4()),
                'title': 'Sample Property 2',
                'description': 'Another beautiful sample property.',
                'price': 150.00,
                'location': 'Sample Location 2'
            }
        ]
        for prop_data in sample_properties:
            Property.objects.create(**prop_data)
        properties = Property.objects.all()
        properties_list = list(properties.values(
            'property_id', 'title', 'description', 'price', 'location', 'created_at'
        ))

    # Store in cache for 1 hour (3600 seconds)
    cache.set('all_properties', properties_list, 3600)

    return {
        "status": "success",
        "status_code": 200,
        "message": "Properties fetched successfully",
        "data": properties_list
    }