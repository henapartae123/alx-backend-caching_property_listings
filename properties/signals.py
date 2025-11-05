from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property


@receiver(post_save, sender=Property)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate all_properties cache when a Property is created or updated.
    """
    cache.delete('all_properties')
    print(f"Cache invalidated: Property '{instance.title}' was saved")


@receiver(post_delete, sender=Property)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate all_properties cache when a Property is deleted.
    """
    cache.delete('all_properties')
    print(f"Cache invalidated: Property '{instance.title}' was deleted")