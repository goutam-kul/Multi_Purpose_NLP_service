from redis import Redis
import json
import logging
from typing import Any, Optional
import os
from datetime import timedelta
from src.config.config import config

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper function for basic operations"""

    _instance = None

    def __new__(cls):
        """Singelton pattern to ensure single redis connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initializes the Redis connection if not already done"""
        if self._initialized:
            return
        
        try: 
            self.client = Redis(
                host=config.redis["host"],
                port=config.redis["port"],
                db=config.redis["db"],
                password=config.redis["password"],
                decode_responses=True
            )
            self.client.ping()  # Test connection
            logger.info("Successfully connected to Redis")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to connect to Redis : {str(e)}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving from Redis: {str(e)}")
            return None

    def set(self, key: str, value: Any, expire: int) -> bool:
        """Set value in Redis with expiration"""
        try:
            return self.client.setex(
                key,
                timedelta(seconds=expire),
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error setting Redis key: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from Redis"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting Redis key: {str(e)}")
            return False

    def flush(self) -> bool:
        """Clear all keys in the current database"""
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logger.error(f"Error flushing Redis db: {str(e)}")
            return False
        