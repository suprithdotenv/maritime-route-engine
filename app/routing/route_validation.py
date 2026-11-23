import logging
from typing import List, Tuple, Dict, Any
from app.geo.spatial_index import spatial_index
from app.geo.geometry import geodesic_distance_km, route_total_distance_km

logger = logging.getLogger(__name__)


class RouteValidator:
    def __init__(self, step_km: float = 15.0):
        self.step_km = step_km

    def validate_route(self, route: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Validate an ordered list of (lon, lat) route waypoints against water geometries.

        Returns a detailed diagnostic validation report.
        """
        if not route or len(route) < 2:
            return {
                "is_valid": False,
                "total_distance_km": 0.0,
                "segment_count": 0,
                "invalid_segments": [],
                "error": "Route must contain at least 2 coordinates."
            }

        invalid_segments = []
        total_dist = 0.0

        for i in range(len(route) - 1):
            p1 = route[i]
            p2 = route[i + 1]
            seg_dist = geodesic_distance_km(p1, p2)
            total_dist += seg_dist

            is_valid = spatial_index.is_edge_valid(p1, p2, max_step_km=self.step_km)
            if not is_valid:
                invalid_segments.append({
                    "segment_index": i,
                    "from_coord": p1,
                    "to_coord": p2,
                    "distance_km": round(seg_dist, 2),
                    "reason": "Segment traverses land or unnavigable area."
                })

        is_route_valid = (len(invalid_segments) == 0)

        return {
            "is_valid": is_route_valid,
            "total_distance_km": round(total_dist, 2),
            "segment_count": len(route) - 1,
            "invalid_segments": invalid_segments,
            "error": None if is_route_valid else f"{len(invalid_segments)} segment(s) cross land."
        }


# Singleton instance
route_validator = RouteValidator()
