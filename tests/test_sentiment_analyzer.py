import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_empty_input():
    """Test empty input text"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": ""}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("length" in str(error).lower() for error in data["detail"])

def test_whitespace_input():
    """Test whitespace-only input"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "   "}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("empty" in str(error).lower() for error in data["detail"])

def test_too_long_input():
    """Test text exceeding max length"""
    long_text = "a" * 1001  # Exceeds 1000 char limit
    response = client.post(
        "/api/v1/sentiment",
        json={"text": long_text}
    )
    assert response.status_code == 422
    data = response.json()
    assert any("length" in str(error).lower() for error in data["detail"])

def test_invalid_input_type():
    """Test non-string input"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": 123}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("string" in str(error).lower() for error in data["detail"])

def test_successful_analysis():
    """Test successful sentiment analysis"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "I love this product!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert "explanation" in data
    assert data["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert 0 <= data["confidence"] <= 1

def test_negative_sentiment():
    """Test negative sentiment"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "I hate this product, it's terrible!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "NEGATIVE"
    assert 0 <= data["confidence"] <= 1

def test_neutral_sentiment():
    """Test neutral sentiment"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "The product is average."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert 0 <= data["confidence"] <= 1

def test_special_characters():
    """Test input with special characters"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "!@#$%^&*()_+ Hello 你好"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data