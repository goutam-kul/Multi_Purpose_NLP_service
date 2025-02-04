import hashlib
import logging
from typing import Optional, Any
from functools import wraps
from .redis_client import RedisClient
from src.config.config import config

logger = logging.getLogger(__name__)

class CacheConfig:
    """Cache configuration settings"""
    DEFAULT_EXPIRE = config.cache_timeouts["default"]
    SENTIMENT_EXPIRE = config.cache_timeouts["sentiment"]
    NER_EXPIRE = config.cache_timeouts["ner"]
    SUMMARIZE_EXPIRE = config.cache_timeouts["summarize"]
    CLASSIFY_EXPIRE = config.cache_timeouts["classify"]
    TEST_EXPIRE = 2  # Keep this for testing

    
class CacheManager:
    """Manager class for handling caching operations"""
    
    def __init__(self):
        """Initialize Redis client"""
        self.redis = RedisClient()

    def generate_key(self, prefix: str, text: str, options: Optional[dict] = None) -> str:
        """
        Generate a unique cache key based on input parameters
        """
        # Create a string combining all parameters
        key_parts = [text]
        if options:
            # Sort the options dict to ensure consistent keys
            key_parts.extend(f"{k}:{v}" for k, v in sorted(options.items()))
            
        # Create hash of the combined string
        key_string = '|'.join(key_parts)
        hash_object = hashlib.md5(key_string.encode())
        hash_value = hash_object.hexdigest()
        
        return f"{prefix}:{hash_value}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self.redis.get(key)

    def set(self, key: str, value: Any, expire: int = CacheConfig.DEFAULT_EXPIRE) -> bool:
        """Set value in cache with expiration"""
        return self.redis.set(key, value, expire)

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return self.redis.delete(key)

def cache_response(prefix: str, expire: int = CacheConfig.DEFAULT_EXPIRE):
    """
    Decorator for caching NLP service responses
    
    Args:
        prefix: Cache key prefix for the service
        expire: Cache expiration time in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, text: str, options: Optional[dict] = None):
            try:
                # Initialize cache manager if not already done
                if not hasattr(self, '_cache_manager'):
                    self._cache_manager = CacheManager()
                
                # Generate cache key
                cache_key = self._cache_manager.generate_key(prefix, text, options)
                
                # Try to get from cache
                cached_result = self._cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.info(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # If not in cache, call original function
                result = func(self, text, options)
                
                # Store in cache
                self._cache_manager.set(cache_key, result, expire)
                logger.info(f"Stored in cache: {cache_key}")
                
                return result
            except Exception as e:
                logger.error(f"Cache error, falling back to original function: {str(e)}")
                return func(self, text, options)
                
        return wrapper
    return decorator