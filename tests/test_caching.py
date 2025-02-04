import pytest
import time
from src.models.sentiment_analyzer import SentimentAnalyzer
from src.cache.cache_manager import CacheManager, CacheConfig

@pytest.fixture
def sentiment_analyzer():
    return SentimentAnalyzer()

@pytest.fixture
def cache_manager():
    return CacheManager()

def test_cache_hit(sentiment_analyzer, cache_manager):
    """Test that identical requests use cached results"""
    test_text = "I love this product!"

    # First call - should not be cached
    start_time = time.time()
    first_result = sentiment_analyzer.analyze(test_text)
    first_duration = time.time() - start_time

    # Second call - should be cached
    start_time = time.time()
    second_result = sentiment_analyzer.analyze(test_text)
    second_duration = time.time() - start_time


    # Verify results are identical
    assert first_result == second_result

    # Second call should be significantly faster than first call
    assert second_duration < first_duration

def test_different_inputs_different_cache(sentiment_analyzer, cache_manager):
    """Test that different inputs use different cache entires"""
    text1 = "I love this product!"
    text2 = "I hate this product!"

    # Analyze both texts
    result1 = sentiment_analyzer.analyze(text1)
    result2 = sentiment_analyzer.analyze(text2)

    # Results should be different
    assert result1 != result2
    assert result1['sentiment'] != result2['sentiment']

def test_cache_expiration(sentiment_analyzer, cache_manager):
    """Test cache expiration (Note: This test takes a few seconds)"""
    test_text = "This is a test of cache expiration"


    # Set very short expiration time
    sentiment_analyzer.analyze(test_text)

    # Verify it's in cache
    cache_key = cache_manager.generate_key("sentiment", test_text)
    assert cache_manager.get(cache_key) is not None

    # Wait for cache to expire 
    time.sleep(CacheConfig.TEST_EXPIRE + 1)  # Wait +1 second than test expire 

    # Verify it's expired 
    assert cache_manager.get(cache_key) is None

    # Getting new results should take longer as it needs to call the inference point again
    start_time = time.time()
    new_result = sentiment_analyzer.analyze(test_text)
    duration = time.time() - start_time

    # Duration should be longer as cache expired
    assert duration > CacheConfig.TEST_EXPIRE + 1  # Assuming cache response takes 1 second

