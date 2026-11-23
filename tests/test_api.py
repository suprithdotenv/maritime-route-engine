import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_root():
    """Test GET / endpoint returns metadata and supported capabilities."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "VoyageIQ" in data["app_name"]
    assert data["status"] == "online"
    assert len(data["supported_functionality"]) > 0


def test_api_health():
    """Test GET /health endpoint returns dataset and graph readiness."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["data_loaded"] is True
    assert data["features_count"] > 50000
    assert data["graph_loaded"] is True
    assert data["graph_nodes"] > 2000


def test_api_route_success():
    """Test POST /route returns valid maritime route coordinates and distances."""
    payload = {
        "origin": {"lon": 72.85, "lat": 18.95},        # Mumbai
        "destination": {"lon": 55.20, "lat": 25.20},   # Dubai
        "refinement_level": 1
    }
    response = client.post("/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["route_found"] is True
    assert data["total_distance_km"] > 1500.0
    assert len(data["coordinates"]) >= 2
    assert data["refinement_level_reached"] == 1


def test_api_route_debug():
    """Test POST /route/debug returns diagnostic breakdown."""
    payload = {
        "origin": {"lon": 72.85, "lat": 18.95},
        "destination": {"lon": 55.20, "lat": 25.20},
        "refinement_level": 1
    }
    response = client.post("/route/debug", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["route_found"] is True
    assert "debug" in data
    assert "coarse_route" in data["debug"]
    assert "refined_route" in data["debug"]
    assert "computation_time_ms" in data["debug"]


def test_api_invalid_coordinates_rejected():
    """Test that coordinates outside [-180, 180] or [-90, 90] trigger HTTP 422."""
    payload = {
        "origin": {"lon": 250.0, "lat": 18.95},
        "destination": {"lon": 55.20, "lat": 25.20},
        "refinement_level": 1
    }
    response = client.post("/route", json=payload)
    assert response.status_code == 422


def test_api_deep_inland_coordinates():
    """Test that points in deep inland deserts return route_found=False with diagnostic explanation."""
    payload = {
        "origin": {"lon": 20.0, "lat": 20.0},          # Deep Sahara Desert
        "destination": {"lon": 72.85, "lat": 18.95},
        "refinement_level": 1
    }
    response = client.post("/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["route_found"] is False
    assert "inland" in data["error_detail"].lower()
