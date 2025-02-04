from src.cache.redis_client import RedisClient
from src.config.config import config
from src.models.sentiment_analyzer import SentimentAnalyzer
from src.models.ner_analyzer import NERAnalyzer


def test_config():
    # Try Redis connection
    try: 
        redis_client = RedisClient()
        print("✅ Redis connection successful")
        print(f"Connected to: {config.redis['host']}:{config.redis['port']}")
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")

    # Test model configurations
    try: 
        sentiment = SentimentAnalyzer()
        print(f"✅ Sentiment model loaded: {sentiment.model}")
    except Exception as e:
        print(f"❌ Sentiment model failed: {str(e)}")

    try:
        ner = NERAnalyzer()
        print("✅ NER model loaded")
    except Exception as e:
        print(f"❌ NER model failed: {str(e)}")

    # Print current configuration
    print("\nCurrent Configs:")
    print(f"Cache Timeouts: {config.cache_timeouts}")
    print(f"Model Paths: {config.model_paths}")
    print(f"Ollam Host: {config.ollama_host}")

if __name__ == "__main__":
    test_config()