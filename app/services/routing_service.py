import logging
import time
from typing import Dict, Any, Tuple, List, Optional
from shapely.geometry import box, Point

from app.core.config import settings
from app.geo.geometry import geodesic_distance_km, route_total_distance_km
from app.geo.spatial_index import spatial_index
from app.routing.global_graph import global_graph
from app.routing.local_routing import connect_point_to_graph, disconnect_point_from_graph
from app.routing.shortest_path import find_shortest_path
from app.routing.regional_refinement import regional_refiner
from app.routing.route_validation import route_validator
from app.routing.chokepoints import get_supported_chokepoints, check_for_chokepoint_limitation

logger = logging.getLogger(__name__)


class RoutingService:
    def __init__(self):
        self.global_graph = global_graph
        self.refiner = regional_refiner
        self.validator = route_validator

    def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        refinement_level: int = 1,
        include_debug: bool = False
    ) -> Dict[str, Any]:
        """Compute the shortest maritime route between origin and destination with regional refinement."""
        t_start = time.time()
        warnings = []
        diagnostics = {}

        # 1. Geographic input validation
        lon1, lat1 = origin
        lon2, lat2 = destination

        if not (-180.0 <= lon1 <= 180.0 and -90.0 <= lat1 <= 90.0):
            raise ValueError(f"Origin coordinates ({lon1}, {lat1}) out of valid geographic range.")
        if not (-180.0 <= lon2 <= 180.0 and -90.0 <= lat2 <= 90.0):
            raise ValueError(f"Destination coordinates ({lon2}, {lat2}) out of valid geographic range.")

        # Check for known chokepoint limitations (e.g. Panama Canal)
        limitation_warnings = check_for_chokepoint_limitation(origin, destination)
        warnings.extend(limitation_warnings)

        # 2. Snap origin & destination to navigable water
        try:
            snapped_orig, orig_ok = spatial_index.snap_to_water(lon1, lat1)
            if not orig_ok:
                return self._failure_response(
                    origin, destination,
                    "Origin coordinate is situated inland and could not be mapped to navigable water.",
                    warnings, diagnostics
                )
        except Exception as e:
            return self._failure_response(origin, destination, f"Origin validation error: {str(e)}", warnings, diagnostics)

        try:
            snapped_dest, dest_ok = spatial_index.snap_to_water(lon2, lat2)
            if not dest_ok:
                return self._failure_response(
                    origin, destination,
                    "Destination coordinate is situated inland and could not be mapped to navigable water.",
                    warnings, diagnostics
                )
        except Exception as e:
            return self._failure_response(origin, destination, f"Destination validation error: {str(e)}", warnings, diagnostics)

        # 3. Direct line-of-sight test (for very close or unobstructed open-water points)
        direct_dist = geodesic_distance_km(snapped_orig, snapped_dest)
        if direct_dist < 400.0 and spatial_index.is_edge_valid(snapped_orig, snapped_dest, max_step_km=15.0):
            direct_route = [snapped_orig, snapped_dest]
            res = {
                "route_found": True,
                "coordinates": direct_route,
                "total_distance_km": round(direct_dist, 2),
                "global_nodes_count": 2,
                "global_edges_count": 1,
                "regional_nodes_count": 2,
                "regional_edges_count": 1,
                "refinement_level_reached": refinement_level,
                "traversed_chokepoints": [],
                "warnings": warnings,
            }
            if include_debug:
                res["debug"] = {
                    "coarse_route": direct_route,
                    "refined_route": direct_route,
                    "computation_time_ms": round((time.time() - t_start) * 1000, 2),
                    "direct_line_of_sight": True,
                    "narrow_passages_preserved": []
                }
            return res

        # 4. Connect to global routing graph
        G = self.global_graph.graph
        global_node_count = G.number_of_nodes()
        global_edge_count = G.number_of_edges()

        try:
            p_orig, orig_conns = connect_point_to_graph(G, snapped_orig)
            p_dest, dest_conns = connect_point_to_graph(G, snapped_dest)
        except Exception as e:
            return self._failure_response(origin, destination, f"Error connecting ports to routing graph: {str(e)}", warnings, diagnostics)

        if len(orig_conns) == 0:
            disconnect_point_from_graph(G, p_orig)
            disconnect_point_from_graph(G, p_dest)
            return self._failure_response(
                origin, destination,
                "Origin port could not be connected to the global water network without crossing land.",
                warnings, diagnostics
            )

        if len(dest_conns) == 0:
            disconnect_point_from_graph(G, p_orig)
            disconnect_point_from_graph(G, p_dest)
            return self._failure_response(
                origin, destination,
                "Destination port could not be connected to the global water network without crossing land.",
                warnings, diagnostics
            )

        # 5. Compute coarse global route
        coarse_path, coarse_dist = find_shortest_path(G, p_orig, p_dest)

        # Disconnect temporary query nodes immediately
        disconnect_point_from_graph(G, p_orig)
        disconnect_point_from_graph(G, p_dest)

        if not coarse_path or len(coarse_path) < 2:
            return self._failure_response(
                origin, destination,
                "No navigable maritime path found between origin and destination in the represented water geometry. "
                "The ports may reside in disconnected water bodies or require an unsupported canal passage.",
                warnings, diagnostics
            )

        # 6. Detect traversed chokepoints
        traversed_chokepoints = self._detect_traversed_chokepoints(coarse_path)

        # 7. Regional Refinement
        refinement_result = self.refiner.refine_route(
            coarse_route=coarse_path,
            refinement_level=refinement_level
        )

        refined_route = refinement_result["refined_route"]
        refined_distance = refinement_result["distance_km"]

        # 8. Validation check
        val_report = self.validator.validate_route(refined_route)
        if not val_report["is_valid"]:
            logger.warning(f"Refined route validation flagged issues: {val_report['invalid_segments']}")
            warnings.append("Notice: Some segments were flagged during rigorous edge validation.")

        computation_time_ms = round((time.time() - t_start) * 1000, 2)

        response = {
            "route_found": True,
            "coordinates": refined_route,
            "total_distance_km": refined_distance,
            "global_nodes_count": global_node_count,
            "global_edges_count": global_edge_count,
            "regional_nodes_count": refinement_result["node_count"],
            "regional_edges_count": refinement_result["edge_count"],
            "refinement_level_reached": refinement_result["refinement_level"],
            "traversed_chokepoints": traversed_chokepoints,
            "warnings": warnings,
        }

        if include_debug:
            response["debug"] = {
                "coarse_route": coarse_path,
                "coarse_distance_km": round(coarse_dist, 2),
                "refined_route": refined_route,
                "global_nodes_count": global_node_count,
                "global_edges_count": global_edge_count,
                "regional_nodes_count": refinement_result["node_count"],
                "regional_edges_count": refinement_result["edge_count"],
                "validation_report": val_report,
                "computation_time_ms": computation_time_ms,
                "narrow_passages_preserved": traversed_chokepoints
            }

        return response

    def _detect_traversed_chokepoints(self, path: List[Tuple[float, float]]) -> List[str]:
        """Identify which registered chokepoints or straits were crossed by the route."""
        traversed = set()
        chokepoints = get_supported_chokepoints()

        for chk_key, chk_data in chokepoints.items():
            b = chk_data["bbox"]
            b_geom = box(b[0], b[1], b[2], b[3])
            # Check if any waypoint in path is inside the chokepoint bbox
            for pt in path:
                if b_geom.contains(Point(pt)):
                    traversed.add(chk_data["name"])
                    break

        return sorted(list(traversed))

    def _failure_response(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        reason: str,
        warnings: List[str],
        diagnostics: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "route_found": False,
            "coordinates": [],
            "total_distance_km": 0.0,
            "global_nodes_count": self.global_graph.graph.number_of_nodes() if self.global_graph._graph else 0,
            "global_edges_count": self.global_graph.graph.number_of_edges() if self.global_graph._graph else 0,
            "regional_nodes_count": 0,
            "regional_edges_count": 0,
            "refinement_level_reached": 0,
            "traversed_chokepoints": [],
            "warnings": warnings,
            "error_detail": reason
        }


# Singleton instance
routing_service = RoutingService()
