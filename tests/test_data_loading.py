import pytest
from shapely.geometry import Point
from app.geo.data_loader import data_loader
from app.geo.spatial_index import spatial_index


def test_data_loading_and_crs():
    """Verify that water polygon geometries load correctly and CRS is EPSG:4326."""
    geoms = data_loader.geometries
    assert geoms is not None
    assert len(geoms) > 50000
    assert "4326" in data_loader.crs


def test_sample_geometry_validity():
    """Verify that sample water polygons in the dataset are valid Shapely geometries."""
    geoms = data_loader.geometries
    # Verify first 100 geometries
    for i in range(100):
        g = geoms[i]
        assert g.is_valid or g.buffer(0).is_valid
        assert g.geom_type in ["Polygon", "MultiPolygon"]


def test_water_vs_land_classification():
    """Test spatial index point containment: open ocean must be True, inland desert must be False."""
    spatial_index.initialize()

    # Open water points
    assert spatial_index.is_point_in_water(0.0, 0.0) is True  # Atlantic
    assert spatial_index.is_point_in_water(70.0, 0.0) is True  # Indian Ocean
    assert spatial_index.is_point_in_water(-170.0, 0.0) is True  # Pacific Ocean

    # Inland points
    assert spatial_index.is_point_in_water(20.0, 20.0) is False  # Sahara Desert
    assert spatial_index.is_point_in_water(10.0, 50.0) is False  # Central Europe
    assert spatial_index.is_point_in_water(78.0, 22.0) is False  # Central India
