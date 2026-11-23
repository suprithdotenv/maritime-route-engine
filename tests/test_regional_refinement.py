import pytest
from app.routing.regional_refinement import regional_refiner
from app.geo.geometry import create_corridor_polygon, route_total_distance_km
from app.routing.route_validation import route_validator


def test_corridor_polygon_generation():
    """Verify corridor polygon creates a valid buffer around route coordinates."""
    route = [(70.0, 15.0), (75.0, 10.0), (80.0, 5.0)]
    corridor = create_corridor_polygon(route, buffer_km=150.0)
    assert corridor.is_valid
    assert not corridor.is_empty
    # Bounds should exceed original line bounds
    minx, miny, maxx, maxy = corridor.bounds
    assert minx < 70.0
    assert maxx > 80.0


def test_regional_refinement_improves_or_preserves_route():
    """Verify regional refinement produces a valid route with shorter or equal distance."""
    # Synthetic coarse route in open Arabian Sea
    coarse = [(65.0, 15.0), (68.5, 12.0), (72.0, 10.0)]
    coarse_dist = route_total_distance_km(coarse)

    result = regional_refiner.refine_route(coarse, refinement_level=1)
    refined = result["refined_route"]
    refined_dist = result["distance_km"]

    assert len(refined) >= 2
    assert refined_dist <= coarse_dist + 1e-3  # refined path is shorter or equal

    # Validate that refined route has zero land crossings
    val = route_validator.validate_route(refined)
    assert val["is_valid"] is True
