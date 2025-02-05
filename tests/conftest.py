import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.router import models
from src.cache.cache_manager import CacheManager

# Client fixture
@pytest.fixture
def client():
    """Create a test client instance"""
    return TestClient(app)


# Cache clean up fixture
@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test"""
    cache_manager = CacheManager()
    cache_manager.redis.flush()
    yield
    cache_manager.redis.flush()

@pytest.fixture(autouse=True)
def cleanup_models():
    """Clean up models after each set"""
    yield
    models.cleanup()

    