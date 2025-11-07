import redis
import json
from app.config import Config

# Initialize Redis client
try:
    redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

def cache_get(key: str):
    """Get value from cache"""
    if not redis_client:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"Cache get error: {e}")
    
    return None

def cache_set(key: str, value: dict, ttl: int = None):
    """Set value in cache with optional TTL"""
    if not redis_client:
        return False
    
    try:
        ttl = ttl or Config.CACHE_TTL
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

def cache_delete(key: str):
    """Delete key from cache"""
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False
