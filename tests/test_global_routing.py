import pytest
from app.routing.global_graph import global_graph
from app.geo.spatial_index import spatial_index
from app.geo.geometry import geodesic_distance_km
from app.routing.local_routing import connect_point_to_graph, disconnect_point_from_graph
from app.routing.shortest_path import find_shortest_path


def test_global_graph_structure():
    """Verify global routing graph has expected size and connectivity."""
    G = global_graph.graph
    assert G.number_of_nodes() > 2000
    assert G.number_of_edges() > 5000

    # Verify edge weights are strictly positive distances
    for u, v, data in G.edges(data=True):
        assert data["weight"] > 0.0


def test_land_crossing_edges_rejected():
    """Verify that direct edges crossing landmasses are strictly rejected."""
    # Direct line from Mumbai (72.8, 18.9) to Chennai (80.3, 13.1) cuts directly across the Indian subcontinent land
    p_mumbai = (72.8, 18.9)
    p_chennai = (80.3, 13.1)
    assert spatial_index.is_edge_valid(p_mumbai, p_chennai) is False

    # Direct line from Red Sea (38.0, 20.0) to Mediterranean (30.0, 32.0) across Egypt desert land
    p_red_sea = (38.0, 20.0)
    p_med = (30.0, 32.0)
    assert spatial_index.is_edge_valid(p_red_sea, p_med) is False

    # Direct line across Africa (Atlantic to Indian Ocean)
    assert spatial_index.is_edge_valid((10.0, 0.0), (45.0, 0.0)) is False


def test_connected_water_route():
    """Verify route computation between two points in connected open ocean."""
    G = global_graph.graph

    # Point off Mumbai and point off Colombo (Sri Lanka)
    orig = (71.5, 18.0)
    dest = (79.0, 6.5)

    p_orig, conns1 = connect_point_to_graph(G, orig)
    p_dest, conns2 = connect_point_to_graph(G, dest)

    assert len(conns1) > 0
    assert len(conns2) > 0

    path, dist = find_shortest_path(G, p_orig, p_dest)
    disconnect_point_from_graph(G, p_orig)
    disconnect_point_from_graph(G, p_dest)

    assert path is not None
    assert len(path) >= 2
    assert 1000.0 < dist < 2500.0
