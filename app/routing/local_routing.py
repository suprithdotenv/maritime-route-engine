import logging
from typing import Tuple, List, Optional
import networkx as nx
from shapely.geometry import Point
from shapely.strtree import STRtree

from app.geo.spatial_index import spatial_index
from app.geo.geometry import geodesic_distance_km

logger = logging.getLogger(__name__)


def connect_point_to_graph(
    graph: nx.Graph,
    point: Tuple[float, float],
    node_tree: Optional[STRtree] = None,
    max_search_km: float = 600.0,
    k_nearest: int = 5
) -> Tuple[Tuple[float, float], List[Tuple[float, float]]]:
    """Connect an arbitrary point (e.g. origin or destination port) to a routing graph.

    Snaps the point to navigable water if necessary, validates candidate edges to avoid
    crossing land, and adds the temporary edges to the graph.

    Returns:
        (snapped_point, connected_neighbors)
    """
    # 1. Snap to water if slightly on land/dock
    snapped, in_water = spatial_index.snap_to_water(point[0], point[1])
    if not in_water:
        raise ValueError(
            f"Point ({point[0]:.4f}, {point[1]:.4f}) is located on land and could not be "
            f"snapped to navigable water within the configured port search radius."
        )

    # Use rounded coord ONLY if rounded coord remains in water; else keep snapped precision
    candidate_round = (round(snapped[0], 4), round(snapped[1], 4))
    if spatial_index.is_point_in_water(candidate_round[0], candidate_round[1]):
        snapped = candidate_round
    else:
        snapped = (snapped[0], snapped[1])

    if snapped in graph and graph.degree(snapped) > 0:
        return snapped, list(graph.neighbors(snapped))

    # Add node to graph
    graph.add_node(snapped, node_type="query_port")

    all_nodes = [n for n in graph.nodes if n != snapped]
    if len(all_nodes) == 0:
        return snapped, []

    # Sort nodes by geodesic distance
    sorted_nodes = sorted(
        all_nodes,
        key=lambda n: geodesic_distance_km(snapped, n)
    )

    connected = []
    # Test candidates up to max_search_km
    for n in sorted_nodes[:25]:
        dist_km = geodesic_distance_km(snapped, n)
        if dist_km > max_search_km and len(connected) >= 1:
            break

        # Validate edge
        if spatial_index.is_edge_valid(snapped, n, max_step_km=15.0):
            graph.add_edge(snapped, n, weight=dist_km, edge_type="port_connector")
            connected.append(n)
            if len(connected) >= k_nearest:
                break

    # If no connection found within max_search_km, try larger radius for isolated ports
    if len(connected) == 0:
        for n in sorted_nodes[25:60]:
            dist_km = geodesic_distance_km(snapped, n)
            if dist_km > 1200.0:
                break
            if spatial_index.is_edge_valid(snapped, n, max_step_km=20.0):
                graph.add_edge(snapped, n, weight=dist_km, edge_type="port_connector")
                connected.append(n)
                if len(connected) >= 2:
                    break

    return snapped, connected


def disconnect_point_from_graph(graph: nx.Graph, point: Tuple[float, float]):
    """Remove a temporary query node and its connected edges from the graph."""
    if point in graph and graph.nodes[point].get("node_type") == "query_port":
        graph.remove_node(point)
