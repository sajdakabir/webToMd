import json
from app.config import Config

# Initialize Redis client (optional)
redis_client = None
try:
    import redis
    redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    print("Redis cache enabled")
except Exception as e:
    print(f"Redis disabled (will work without caching): {e}")
    redis_client = None

def cache_get(key: str):
    """Get value from cache"""
    if not redis_client:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception:
        pass  # Silent fail - caching is optional
    
    return None

def cache_set(key: str, value: dict, ttl: int = None):
    """Set value in cache with optional TTL"""
    if not redis_client:
        return False
    
    try:
        ttl = ttl or Config.CACHE_TTL
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        pass  # Silent fail - caching is optional
        return False

def cache_delete(key: str):
    """Delete key from cache"""
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception:
        pass  # Silent fail - caching is optional
        return False
