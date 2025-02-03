import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# def test_empty_input():
#     """Test empty input text"""
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": ""}
#     )
#     assert response.status_code == 422
#     data = response.json()
#     assert "detail" in data
#     assert any("length" in str(error).lower() for error in data["detail"])

# def test_whitespace_input():
#     """Test whitespace-only input"""
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": "   "}
#     )
#     assert response.status_code == 422
#     data = response.json()
#     assert "detail" in data
#     assert any("empty" in str(error).lower() for error in data["detail"])

# def test_invalid_input_type():
#     """Test non-string input"""
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": 123}
#     )
#     assert response.status_code == 422
#     data = response.json()
#     assert "detail" in data
#     assert any("string" in str(error).lower() for error in data["detail"])

# def test_successful_classification():
#     """Test successful classification"""
#     test_text = "Tesla announces new electric vehicle battery technology"
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": test_text}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert all(k in data for k in ["text", "primary_category", "confidence", "all_categories", "explanation"])
#     assert data["text"] == test_text
#     assert isinstance(data["primary_category"], str)
#     assert 0 <= data["confidence"] <= 1
#     assert isinstance(data["all_categories"], list)
#     assert len(data["all_categories"]) > 0
#     for category in data["all_categories"]:
#         assert isinstance(category["category"], str)
#         assert isinstance(category["confidence"], float)
#         assert 0 <= category["confidence"] <= 1
#     assert isinstance(data["explanation"], str)

# def test_custom_categories():
#     """Test classification with custom categories"""
#     test_text = "Breaking news: Major earthquake hits Pacific region"
#     response = client.post(
#         "/api/v1/classify",
#         json={
#             "text": test_text,
#             "options": {
#                 "categories": ["Natural Disaster", "Politics", "Sports"],
#                 "multi_label": False
#             }
#         }
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["text"] == test_text
#     assert data["primary_category"] in ["Natural Disaster", "Politics", "Sports"]
#     assert all(k in data for k in ["text", "primary_category", "confidence", "all_categories", "explanation"])
    
# def test_multi_label_classification():
#     """Test multi-label classification"""
#     test_text = "Apple announces new AI-powered iPhone features"
#     response = client.post(
#         "/api/v1/classify",
#         json={
#             "text": test_text,
#             "options": {"multi_label": True}
#         }
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["text"] == test_text
#     assert all(k in data for k in ["text", "primary_category", "confidence", "all_categories", "explanation"])
#     assert len(data["all_categories"]) >= 1
#     for category in data["all_categories"]:
#         assert "category" in category
#         assert "confidence" in category
#         assert 0 <= category["confidence"] <= 1

def test_confidence_scores():
    """Test confidence scores are valid"""
    test_text = "SpaceX launches new satellite into orbit"
    response = client.post(
        "/api/v1/classify",
        json={"text": test_text}
    )
    assert response.status_code == 200
    data = response.json()
    print("Response:\n", data)
    assert data["text"] == test_text
    assert all(k in data for k in ["text", "primary_category", "confidence", "all_categories", "explanation"])
    assert 0 <= data["confidence"] <= 1
    for category in data["all_categories"]:
        assert 0 <= category["confidence"] <= 1

# def test_special_characters():
#     """Test input with special characters"""
#     test_text = "Company's Q3 profit rises 15% to $1.2B!"
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": test_text}
#     )
#     print("\nResponse for special characters:", response.json())  # Add this debug line
#     assert response.status_code == 200


# def test_multilingual():
#     """Test multilingual input"""
#     test_text = "Toyota launches 新型車 in the global market"
#     response = client.post(
#         "/api/v1/classify",
#         json={"text": test_text}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["text"] == test_text
#     assert all(k in data for k in ["text", "primary_category", "confidence", "all_categories", "explanation"])