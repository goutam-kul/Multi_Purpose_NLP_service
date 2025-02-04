# Contains all configuration class
# Loads values from env. variables
# Falls back to default values if env vars  aren't set
# Provides type checking and validation
# Used throughout the application to accesss settings
"""Configuration management for NLP service"""

import os 
from typing import Dict, Any
from src.config.default import (
    MODEL_PATHS,
    OLLAMA_HOST,
    CACHE_TIMEOUT,
    API_CONFIG,
    REDIS_CONFIG
)

class Config:
    """Config class for NLP service"""
    
    def __init__(self):
        self.model_paths = self._load_model_paths()
        self.ollama_host = self._get_env("OLLAMA_HOST", OLLAMA_HOST)
        self.cache_timeouts = self._load_cache_timeouts()
        self.redis = self._load_redis_config()
        self.api = self._load_api_config()

    def _get_env(self, key: str, default: Any) -> Any:
        """Get env vars with fallback to default"""
        return os.getenv(key=key, default=default)

    def _load_model_paths(self) -> Dict[str, str]:
        """Load model paths from env or defaults"""
        return {
            "ner": self._get_env("NER_MODEL_PATH", MODEL_PATHS["ner"]),
            "sentiment": self._get_env("SENTIMENT_MODEL_PATH", MODEL_PATHS["sentiment"]),
            "summarize": self._get_env("SUMMARIZE_MODEL_PATH", MODEL_PATHS["summarize"]),
            "classify": self._get_env("CLASSIFY_MODEL_PATH", MODEL_PATHS["classify"])
        }
    
    def _load_cache_timeouts(self) -> Dict[str, int]:
        """Load cache timeouts settings"""
        return {
            "default": int(self._get_env("CACHE_DEFAULT_TIMEOUT", CACHE_TIMEOUT["default"])),
            "sentiment": int(self._get_env("CACHE_SENTIMENT_TIMEOUT", CACHE_TIMEOUT["sentiment"])),
            "ner": int(self._get_env("CACHE_NER_TIMEOUT", CACHE_TIMEOUT["ner"])),
            "summarize": int(self._get_env("CACHE_SUMMARIZE_TIMEOUT", CACHE_TIMEOUT["summarize"])),
            "classify": int(self._get_env("CACHE_CLASSIFY_TIMEOUT", CACHE_TIMEOUT["classify"]))
        }
    
    def _load_redis_config(self) -> Dict[str, Any]:
        """Load redis configuration"""
        return {
            "host": self._get_env("REDIS_HOST", REDIS_CONFIG["host"]),
            "port": int(self._get_env("REDIS_PORT", REDIS_CONFIG["port"])),
            "db": int(self._get_env("REDIS_DB", REDIS_CONFIG["db"])),
            "password": self._get_env("REDIS_PASSWORD", REDIS_CONFIG["password"])
        }
    
    def _load_api_config(self) -> Dict[str, Any]:
        """Load API configuration"""
        return {
            "max_request_size": int(self._get_env("API_MAX_REQUEST_SIZE", API_CONFIG["max_request_size"])),
            "request_timeout": int(self._get_env("API_REQUEST_TIMEOUT", API_CONFIG["request_timeout"])),
            "rate_limit": int(self._get_env("API_RATE_LIMIT", API_CONFIG["rate_limit"])) 
        }
    
# Create a singleton instance
config = Config()