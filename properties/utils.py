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


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.

    Returns:
        dict: Dictionary containing cache metrics including:
            - keyspace_hits: Total number of cache hits
            - keyspace_misses: Total number of cache misses
            - hit_ratio: Percentage of successful cache hits
            - total_requests: Total cache requests
    """
    try:
        # Connect to Redis using django-redis
        redis_client = get_redis_connection("default")

        # Get Redis INFO stats
        info = redis_client.info("stats")

        # Extract keyspace hits and misses
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)

        # Calculate total requests and hit ratio
        total_requests = keyspace_hits + keyspace_misses

        if total_requests > 0:
            hit_ratio = (keyspace_hits / total_requests) * 100
        else:
            hit_ratio = 0.0

        # if total_requests > 0 else 0"
        # Prepare metrics dictionary
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': round(hit_ratio, 2)
        }

        # Log metrics
        logger.info(f"Redis Cache Metrics: {metrics}")
        print(f"\n=== Redis Cache Metrics ===")
        print(f"Keyspace Hits: {keyspace_hits}")
        print(f"Keyspace Misses: {keyspace_misses}")
        print(f"Total Requests: {total_requests}")
        print(f"Hit Ratio: {hit_ratio:.2f}%")
        print(f"===========================\n")

        return metrics

    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {str(e)}")
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0.0
        }