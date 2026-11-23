import networkx as nx
from typing import List, Tuple, Optional
from app.geo.geometry import geodesic_distance_km


def find_shortest_path(
    graph: nx.Graph,
    source: Tuple[float, float],
    target: Tuple[float, float]
) -> Tuple[Optional[List[Tuple[float, float]]], float]:
    """Find the shortest path on the graph between source and target using A* with a geodesic distance heuristic.

    Returns:
        (path_coords, total_distance_km)
    """
    if source == target:
        return [source], 0.0

    if source not in graph or target not in graph:
        return None, 0.0

    def heuristic(u: Tuple[float, float], v: Tuple[float, float]) -> float:
        return geodesic_distance_km(u, v)

    try:
        path = nx.astar_path(
            graph,
            source=source,
            target=target,
            heuristic=heuristic,
            weight="weight"
        )
        total_dist = nx.path_weight(graph, path, weight="weight")
        return path, total_dist
    except nx.NetworkXNoPath:
        return None, 0.0
    except Exception:
        # Fallback to Dijkstra
        try:
            path = nx.shortest_path(
                graph,
                source=source,
                target=target,
                weight="weight"
            )
            total_dist = nx.path_weight(graph, path, weight="weight")
            return path, total_dist
        except nx.NetworkXNoPath:
            return None, 0.0
