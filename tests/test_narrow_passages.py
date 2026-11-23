import pytest
from app.services.routing_service import routing_service
from app.routing.route_validation import route_validator


def test_suez_canal_navigation():
    """Critical Requirement: Engine must route through Suez Canal between Asia and Europe instead of Cape of Good Hope."""
    origin = (72.85, 18.95)        # Mumbai, India
    destination = (29.90, 31.20)   # Alexandria / Mediterranean entrance

    res = routing_service.calculate_route(
        origin=origin,
        destination=destination,
        refinement_level=1,
        include_debug=True
    )

    assert res["route_found"] is True
    # The route distance via Suez is ~6,000 - 7,000 km.
    # Routing around the Cape of Good Hope would be >20,000 km.
    assert 5000.0 < res["total_distance_km"] < 8000.0

    # Verify that Suez Canal was detected and traversed
    assert any("Suez Canal" in chk for chk in res["traversed_chokepoints"])

    # Verify geometric validity of all refined coordinates
    val = route_validator.validate_route(res["coordinates"])
    assert val["is_valid"] is True


def test_strait_of_hormuz_navigation():
    """Test routing from Persian Gulf to Arabian Sea through Strait of Hormuz."""
    origin = (55.20, 25.20)        # Dubai / UAE (Persian Gulf)
    destination = (71.50, 18.50)   # Off Mumbai (Arabian Sea)

    res = routing_service.calculate_route(
        origin=origin,
        destination=destination,
        refinement_level=1
    )

    assert res["route_found"] is True
    assert any("Hormuz" in chk for chk in res["traversed_chokepoints"])
    assert 1800.0 < res["total_distance_km"] < 3000.0

    val = route_validator.validate_route(res["coordinates"])
    assert val["is_valid"] is True


def test_strait_of_malacca_navigation():
    """Test routing from South China Sea / Singapore to Indian Ocean through Strait of Malacca."""
    origin = (104.00, 1.40)        # Singapore / East
    destination = (80.50, 13.00)   # Chennai / Bay of Bengal

    res = routing_service.calculate_route(
        origin=origin,
        destination=destination,
        refinement_level=1
    )

    assert res["route_found"] is True
    assert any("Malacca" in chk for chk in res["traversed_chokepoints"])
    assert 2500.0 < res["total_distance_km"] < 4000.0

    val = route_validator.validate_route(res["coordinates"])
    assert val["is_valid"] is True


def test_strait_of_gibraltar_navigation():
    """Test routing from Mediterranean to Atlantic through Strait of Gibraltar."""
    origin = (2.20, 41.35)         # Barcelona, Western Mediterranean
    destination = (-9.20, 38.70)   # Lisbon, Atlantic Ocean

    res = routing_service.calculate_route(
        origin=origin,
        destination=destination,
        refinement_level=1
    )

    assert res["route_found"] is True
    assert any("Gibraltar" in chk for chk in res["traversed_chokepoints"])
    assert 1200.0 < res["total_distance_km"] < 2500.0

    val = route_validator.validate_route(res["coordinates"])
    assert val["is_valid"] is True


def test_panama_canal_limitation_reported():
    """Verify that routing across Americas detects and reports Panama Canal dataset limitation."""
    # Caribbean to Pacific
    origin = (-75.0, 15.0)         # Caribbean Sea
    destination = (-110.0, 20.0)   # Pacific Ocean

    res = routing_service.calculate_route(
        origin=origin,
        destination=destination,
        refinement_level=1
    )

    # Must contain warning regarding Panama Canal limitation
    has_panama_warning = any("Panama Canal" in w for w in res["warnings"])
    assert has_panama_warning is True
