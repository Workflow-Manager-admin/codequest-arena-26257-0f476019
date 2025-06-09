"""
Demo integration test for FastAPI app endpoints (health, features) with TestClient.

Note: These are basic connectivity tests to exercise CI checks and endpoint availability.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


# PUBLIC_INTERFACE
def test_health_check():
    """Test that health check root endpoint returns 200 + expected message."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()
    assert resp.json()["message"] == "Healthy"


# PUBLIC_INTERFACE
def test_features_list():
    """Test that /features endpoint returns features with expected structure."""
    resp = client.get("/features")
    assert resp.status_code == 200
    data = resp.json()
    assert "features" in data
    assert isinstance(data["features"], list)
    assert any("PR Integration" in feat["name"] for feat in data["features"])
