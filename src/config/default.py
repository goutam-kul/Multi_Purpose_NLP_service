# Stores all default configuration values
# Acts as single source of truth for settings
# Makes it easy to see all configurable  value in one place
# Values here can be overriden by env. values
"""Defaul configuration values for NLP service"""

AVAILABLE_MODELS = {
    "llama": "llama3.2:3b",
    "gemma": "gemma2:2b",
    "qwen": "qwen2.5:3b",
    "phi3": "phi3:3.8b"
}

MODEL_PATHS = {
    "ner": AVAILABLE_MODELS["llama"],
    "sentiment": AVAILABLE_MODELS["llama"],
    "summarize": AVAILABLE_MODELS["llama"],
    "classify": AVAILABLE_MODELS["llama"],
}

OLLAMA_HOST = "http://localhost:11434"

# Cache Settings
CACHE_TIMEOUT = {
    "default": 3600,   # 1 hour
    "sentiment": 7200,  # 2 hour
    "ner": 7200,
    "summarize": 7200,
    "classify": 7200,
}

# Redis Settings
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": "Say1234@"
}

# API Settings
API_CONFIG = {
    "max_request_size": 1_00_000,   # 1 MB
    "request_timeout": 30,          # 30 seconds
    "rate_limit": 50               # requests per minute
}
