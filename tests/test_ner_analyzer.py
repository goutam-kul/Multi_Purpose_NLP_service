from tests.conftest import client

def test_empty_input(client):
    """Test empty input text"""
    response = client.post(
        "/api/v1/ner",
        json={"text": ""}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("length" in str(error).lower() for error in data["detail"])

def test_whitespace_input(client):
    """Test whitespace-only input"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "   "}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("empty" in str(error).lower() for error in data["detail"])

def test_too_long_input(client):
    """Test text exceeding max length"""
    long_text = "a" * 2001  # Exceeds 2000 char limit
    response = client.post(
        "/api/v1/ner",
        json={"text": long_text}
    )
    assert response.status_code == 422
    data = response.json()
    assert any("length" in str(error).lower() for error in data["detail"])

def test_single_word(client):
    """Test text with single word"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "John"}
    )
    assert response.status_code == 422
    data = response.json()
    assert any("two words" in str(error).lower() for error in data["detail"])

def test_successful_ner(client):
    """Test successful NER analysis"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "John works at Microsoft in Seattle"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert isinstance(data["entities"], list)
    
    # Check entity structure
    for entity in data["entities"]:
        assert all(k in entity for k in ["text", "type", "start", "end"])
        assert entity["start"] < entity["end"]
        assert isinstance(entity["text"], str)

def test_no_entities(client):
    """Test text with no entities"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "The sun rises in the morning."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert isinstance(data["entities"], list)

def test_special_characters(client):
    """Test input with special characters"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "Mr. O'Connor works at @Twitter!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    for entity in data["entities"]:
        assert all(k in entity for k in ["text", "type", "start", "end"])

def test_multilingual(client):
    """Test multilingual input"""
    response = client.post(
        "/api/v1/ner",
        json={"text": "Zhang Wei works at Alibaba in 北京"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    # Validate entity positions
    for entity in data["entities"]:
        assert entity["start"] < entity["end"]
        assert data["text"][entity["start"]:entity["end"]] == entity["text"]