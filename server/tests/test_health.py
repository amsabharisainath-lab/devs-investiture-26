import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns 200 OK and expected API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "DEVS Investiture API" in data["message"]
    assert "version" in data
    assert data["docs"] == "/api/docs"


def test_health_check_endpoint(client: TestClient):
    """Test the /api/v1/health endpoint returns 200 OK and healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "devs-investiture-api"
    assert "timestamp" in data
