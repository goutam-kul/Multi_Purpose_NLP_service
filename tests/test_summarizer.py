from tests.conftest import client


def test_empty_input(client):
    """Test empty input text"""
    response = client.post(
        "/api/v1/summarize",
        json={"text": ""}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("length" in str(error).lower() for error in data["detail"])

def test_too_short_input(client):
    """Test text shorter than minimum required words"""
    response = client.post(
        "/api/v1/summarize",
        json={"text": "Short text."}
    )
    assert response.status_code == 422
    data = response.json()
    assert any("10 words" in str(error).lower() for error in data["detail"])

def test_invalid_input_type(client):
    """Test non-string input"""
    response = client.post(
        "/api/v1/summarize",
        json={"text": 123}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("string" in str(error).lower() for error in data["detail"])

def test_successful_summarization(client):
    """Test successful summarization"""
    long_text = ("The quick brown fox jumps over the lazy dog. " * 10) + "This makes it long enough for summarization."
    response = client.post(
        "/api/v1/summarize",
        json={"text": long_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(k in data for k in ["summary", "metadata", "key_points"])
    assert data["metadata"]["compression_ratio"] > 0
    assert len(data["summary"]) < len(long_text)

def test_custom_max_length(client):
    """Test summarization with custom max_length"""
    long_text = "The quick brown fox jumps over the lazy dog. " * 10
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": long_text,
            "options": {"max_length": 50}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["summary"].split()) <= 50

def test_abstractive_type(client):
    """Test abstractive summarization"""
    long_text = "The quick brown fox jumps over the lazy dog. " * 10
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": long_text,
            "options": {"type": "abstractive"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["summary_type"] == "abstractive"

def test_special_characters(client):
    """Test input with special characters"""
    text = ("The company's Q3 results showed a 15% increase in revenue. "
            "The CEO stated: \"We're very pleased with these results!\" "
            "Visit us at http://example.com or email us at info@example.com. " * 3)
    response = client.post(
        "/api/v1/summarize",
        json={"text": text}
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "metadata" in data

def test_multilingual(client):
    """Test multilingual input"""
    text = ("The international conference was a success. "
            "Representatives from 好市多 and Volkswagen attended. "
            "They discussed global market trends and future collaborations. " * 3)
    response = client.post(
        "/api/v1/summarize",
        json={"text": text}
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data