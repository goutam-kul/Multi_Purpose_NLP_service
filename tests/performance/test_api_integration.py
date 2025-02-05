from tests.conftest import client
import time 

def test_sentiment_cache_integration(client):
    """Test sentiment analysis API with caching"""
    payload = {"text": "I love this product"}

    # First request - should miss cache
    start_time = time.time()
    response1 = client.post("/api/v1/sentiment", json=payload)
    first_duration = time.time() - start_time

    assert response1.status_code == 200
    first_result = response1.json()

    # Second request - should hit cache
    start_time = time.time()
    response2 = client.post("/api/v1/sentiment", json=payload)
    second_duration = time.time() - start_time

    assert response2.status_code == 200
    second_result = response1.json()

    # Verfiy the response matches
    assert first_result == second_result
    # Verify second request was faster (cached)
    assert second_duration < first_duration

def test_ner_cache_integration(client):
    """Test NER api with caching"""
    payload = {"text": "ISRO successfully test a new space docking system called SpaDex"}

    # First request 
    start_time = time.time()
    response1 = client.post("/api/v1/ner", json=payload)
    first_duration = time.time() - start_time

    assert response1.status_code == 200
    first_result = response1.json()

    # Second request
    start_time = time.time()
    response2 = client.post("/api/v1/ner", json=payload)
    second_duration = time.time() - start_time

    assert response2.status_code == 200
    second_result = response2.json()

    assert first_result == second_result
    assert second_duration < first_duration

def test_summarize_cache_integration(client):
    """Test summarization API with caching"""
    payload = {
        "text": "The quick brown fox jumped over the lazy dog" * 10,
        "options": {"max_length": 50}
    }

    # First request 
    start_time = time.time()
    response1 = client.post("/api/v1/summarize", json=payload)
    first_duration = time.time() - start_time

    assert response1.status_code == 200
    first_result = response1.json()

    # Second request
    start_time = time.time()
    response2 = client.post("/api/v1/summarize", json=payload)
    second_duration = time.time() - start_time

    assert response2.status_code == 200
    second_result = response2.json()

    assert first_result == second_result
    assert second_duration < first_duration
    
def test_classify_cache_integration(client):
    """Test classification API with caching"""
    payload = {
        "text": "Tesla announces new self-driving technology for cars.",
        "options": {"multi_label": True}
    }

    # First request
    start_time = time.time() 
    response1 = client.post("/api/v1/classify", json=payload)
    first_duration = time.time() - start_time

    assert response1.status_code == 200
    first_result = response1.json()

    # Second request - should hit cache
    start_time = time.time()
    response2 = client.post("/api/v1/classify", json=payload)
    second_duration = time.time() - start_time

    assert response2.status_code == 200
    second_result = response2.json()
    
    assert first_result == second_result
    assert second_duration < first_duration