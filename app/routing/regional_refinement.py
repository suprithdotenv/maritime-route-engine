import logging
import time
from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString

from app.core.config import settings
from app.geo.geometry import (
    create_corridor_polygon,
    geodesic_distance_km,
    route_total_distance_km
)
from app.geo.spatial_index import spatial_index
from app.routing.shortest_path import find_shortest_path
from app.routing.chokepoints import get_supported_chokepoints
from shapely.strtree import STRtree

logger = logging.getLogger(__name__)


class RegionalRouteRefiner:
    def __init__(self, buffer_km: float = settings.corridor_buffer_km):
        self.buffer_km = buffer_km

    def refine_route(
        self,
        coarse_route: List[Tuple[float, float]],
        refinement_level: int = 1
    ) -> Dict[str, Any]:
        """Refine a coarse global route within its geographic corridor.

        Increases node density ONLY within the corridor polygon, rebuilds the local
        corridor graph, recomputes the shortest path, and performs line-of-sight smoothing.
        """
        if len(coarse_route) < 2:
            return {
                "refined_route": coarse_route,
                "distance_km": 0.0,
                "node_count": len(coarse_route),
                "edge_count": 0,
                "refinement_level": 0
            }

        t0 = time.time()
        current_route = list(coarse_route)
        total_nodes = 0
        total_edges = 0

        step_sizes = {
            1: [1.2],
            2: [1.2, 0.7],
            3: [1.2, 0.7, 0.4]
        }
        steps_to_run = step_sizes.get(min(refinement_level, 3), [1.2])

        for level_idx, step_deg in enumerate(steps_to_run):
            # 1. Create geographic corridor polygon around current route
            corridor_poly = create_corridor_polygon(current_route, buffer_km=self.buffer_km)
            minx, miny, maxx, maxy = corridor_poly.bounds

            # 2. Sample dense nodes ONLY within the corridor
            G_local = nx.Graph()

            # Always add all current route waypoints preserving exact precision
            for pt in current_route:
                pt_exact = (float(pt[0]), float(pt[1]))
                G_local.add_node(pt_exact, node_type="route_anchor")

            # Add consecutive edges from current route
            for i in range(len(current_route) - 1):
                p1 = (float(current_route[i][0]), float(current_route[i][1]))
                p2 = (float(current_route[i+1][0]), float(current_route[i+1][1]))
                d = geodesic_distance_km(p1, p2)
                G_local.add_edge(p1, p2, weight=d, edge_type="preserved_route")

            # Dense grid within corridor bounding box
            lons = np.arange(minx, maxx + step_deg, step_deg)
            lats = np.arange(miny, maxy + step_deg, step_deg)

            for y in lats:
                for x in lons:
                    pt_geom = Point(x, y)
                    if corridor_poly.contains(pt_geom):
                        if spatial_index.is_point_in_water(x, y):
                            node = (round(float(x), 4), round(float(y), 4))
                            if node not in G_local:
                                G_local.add_node(node, node_type="dense_corridor")

            all_local_nodes = list(G_local.nodes)
            node_pts = [Point(n) for n in all_local_nodes]
            local_tree = STRtree(node_pts)

            # 3. Connect local dense nodes
            max_connect_deg = step_deg * 1.8
            for i, n1 in enumerate(all_local_nodes):
                pt1 = Point(n1)
                candidates = local_tree.query(pt1.buffer(max_connect_deg))
                for c in candidates:
                    if c > i:
                        n2 = all_local_nodes[c]
                        if not G_local.has_edge(n1, n2):
                            d_km = geodesic_distance_km(n1, n2)
                            if d_km < 350.0 and spatial_index.is_edge_valid(n1, n2, max_step_km=10.0):
                                G_local.add_edge(n1, n2, weight=d_km, edge_type="corridor_edge")

            total_nodes = G_local.number_of_nodes()
            total_edges = G_local.number_of_edges()

            # 4. Recompute route through refined graph
            start_node = (float(current_route[0][0]), float(current_route[0][1]))
            end_node = (float(current_route[-1][0]), float(current_route[-1][1]))

            refined_path, dist_km = find_shortest_path(G_local, start_node, end_node)
            if refined_path and len(refined_path) >= 2:
                current_route = refined_path

        # 5. Nautical line-of-sight path smoothing
        smoothed_route = self.smooth_route(current_route)
        final_distance = route_total_distance_km(smoothed_route)

        logger.info(
            f"Regional refinement completed in {time.time()-t0:.2f}s: "
            f"{len(coarse_route)} coarse pts -> {len(smoothed_route)} refined pts, "
            f"distance {final_distance:.1f} km, corridor graph ({total_nodes} nodes, {total_edges} edges)"
        )

        return {
            "refined_route": smoothed_route,
            "distance_km": round(final_distance, 2),
            "node_count": total_nodes,
            "edge_count": total_edges,
            "refinement_level": min(refinement_level, len(steps_to_run))
        }

    def smooth_route(self, route: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Perform line-of-sight shortcutting across open water without violating channel bends."""
        if len(route) <= 2:
            return route

        chokepoint_boxes = [chk["bbox"] for chk in get_supported_chokepoints().values()]

        def is_chokepoint_coord(coord: Tuple[float, float]) -> bool:
            lon, lat = coord
            for b in chokepoint_boxes:
                if b[0] <= lon <= b[2] and b[1] <= lat <= b[3]:
                    return True
            return False

        smoothed = [route[0]]
        curr = 0
        n = len(route)

        while curr < n - 1:
            p_curr = route[curr]

            if is_chokepoint_coord(p_curr):
                smoothed.append(route[curr + 1])
                curr += 1
                continue

            next_idx = curr + 1
            max_lookahead = min(n - 1, curr + 8)
            for candidate in range(max_lookahead, curr + 1, -1):
                p_cand = route[candidate]
                if is_chokepoint_coord(p_cand):
                    continue
                d = geodesic_distance_km(p_curr, p_cand)
                if d < 600.0 and spatial_index.is_edge_valid(p_curr, p_cand, max_step_km=5.0):
                    next_idx = candidate
                    break
            smoothed.append(route[next_idx])
            curr = next_idx

        return smoothed


# Singleton instance
regional_refiner = RegionalRouteRefiner()
