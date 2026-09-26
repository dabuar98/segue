from django.conf import settings
from django.core.cache import cache

# Status of a query while its audio features are computed
PENDING = 'pending'
READY = 'ready'
FAILED = 'failed'

def get_query(query_id):
    """
    Retrieves a query entry from the cache
    Args:
        query_id: identifier of the query (str)

    Returns:
        dict with status, descriptor_set and vector (None once computed), or None if it does not exist or expired

    """
    return cache.get(f"query:{query_id}")


def set_query(query_id, status, descriptor_set, vector=None):
    """
    Stores a query entry in the cache, overwriting any previous entry, for QUERY_TTL seconds
    Args:
        query_id: identifier of the query (str)
        status: one of PENDING, READY, FAILED
        descriptor_set: descriptor set used to compute the vector
        vector: query vector (1xN list), only when status is READY

    """
    entry = {'status': status, 'descriptor_set': descriptor_set, 'vector': vector}
    cache.set(f"query:{query_id}", entry, timeout=settings.QUERY_TTL)


def delete_query(query_id):
    cache.delete(f"query:{query_id}")
