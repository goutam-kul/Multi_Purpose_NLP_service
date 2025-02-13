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
        # Get current model
        current_model = config.get_current_model()
        logging.info(f"Cache key Generation - Current Model: {current_model}")
        # Create a string combining all parameters
        cleaned_text = text.strip().strip('"')

        key_parts = [current_model, cleaned_text]
        if options:
            # Sort the options dict to ensure consistent keys
            key_parts.extend(f"{k}:{v}" for k, v in sorted(options.items()))
            
        # Create hash of the combined string
        key_string = '|'.join(key_parts)
        hash_object = hashlib.md5(key_string.encode())
        hash_value = hash_object.hexdigest()

        final_key = f"{prefix}:{current_model}:{hash_value}"
        logging.info(f"Generated Cache Key: {final_key}")
        return final_key

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
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, text: str, options: Optional[dict] = None):
            try:
                # Initialize cache manager
                if not hasattr(self, '_cache_manager'):
                    self._cache_manager = CacheManager()
                
                # Get current model
                current_model = config.get_current_model()
                print(f"Cache decorator - Using model: {current_model}")  # Debug
                
                # Generate cache key
                cache_key = self._cache_manager.generate_key(prefix, text, options)
                print(f"Cache key generated: {cache_key}")  # Debug
                
                # Try to get from cache
                cached_result = self._cache_manager.get(cache_key)
                
                if cached_result:  # Only check model if we have a cached result
                    print(f"Found cached result for model: {cached_result.get('model', 'unknown')}")  # Debug
                    if cached_result.get('model') == current_model:
                        print("Cache hit - returning cached result")  # Debug
                        return cached_result
                
                # If we get here, either no cache or different model
                print("Cache miss - computing new result")  # Debug
                result = func(self, text, options)
                
                # Add model to result if not present
                if isinstance(result, dict):
                    result['model'] = current_model
                
                # Store in cache
                self._cache_manager.set(cache_key, result, expire)
                return result
                
            except Exception as e:
                print(f"Cache error: {str(e)}")  # Debug
                return func(self, text, options)
                
        return wrapper
    return decorator