import logging
from typing import Tuple, List, Optional
import math
import numpy as np
from shapely.geometry import Point, box, LineString
from shapely.strtree import STRtree
from shapely.ops import nearest_points

from app.geo.data_loader import data_loader
from app.geo.geometry import interpolate_geodesic, geodesic_distance_km
from app.core.config import settings

logger = logging.getLogger(__name__)


class SpatialIndex:
    def __init__(self, loader=data_loader):
        self.loader = loader
        self._tree: Optional[STRtree] = None
        self._geometries: Optional[np.ndarray] = None

    def initialize(self):
        """Build the STRtree spatial index on the water polygons."""
        if self._tree is not None:
            return
        geoms = self.loader.geometries
        self._geometries = geoms
        logger.info(f"Building STRtree over {len(geoms)} water polygons...")
        self._tree = STRtree(geoms)
        logger.info("STRtree built successfully.")

    @property
    def tree(self) -> STRtree:
        if self._tree is None:
            self.initialize()
        return self._tree

    @property
    def geometries(self) -> np.ndarray:
        if self._geometries is None:
            self.initialize()
        return self._geometries

    def is_point_in_water(self, lon: float, lat: float) -> bool:
        """Check if (lon, lat) is strictly inside a navigable water polygon."""
        pt = Point(lon, lat)
        candidates = self.tree.query(pt)
        if len(candidates) == 0:
            return False
        for idx in candidates:
            geom = self.geometries[idx]
            if geom.contains(pt) or geom.distance(pt) < 1e-7:
                return True
        return False

    def is_edge_valid(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        max_step_km: float = settings.edge_validation_step_km
    ) -> bool:
        """Validate whether the geodesic route segment between p1 and p2 traverses only navigable water.

        Rejects any edge that crosses land or invalid areas.
        """
        if not self.is_point_in_water(p1[0], p1[1]):
            return False
        if not self.is_point_in_water(p2[0], p2[1]):
            return False

        pts = interpolate_geodesic(p1, p2, max_step_km=max_step_km)
        for pt_coord in pts[1:-1]:
            if not self.is_point_in_water(pt_coord[0], pt_coord[1]):
                return False

        return True

    def snap_to_water(
        self,
        lon: float,
        lat: float,
        max_radius_deg: float = settings.port_snap_radius_deg
    ) -> Tuple[Tuple[float, float], bool]:
        """If (lon, lat) is already in water, returns it directly.

        Otherwise, searches within max_radius_deg to snap to the nearest navigable water point,
        safely nudged into the water interior.
        """
        if self.is_point_in_water(lon, lat):
            return (lon, lat), True

        pt = Point(lon, lat)
        search_box = box(
            lon - max_radius_deg,
            lat - max_radius_deg,
            lon + max_radius_deg,
            lat + max_radius_deg
        )
        candidates = self.tree.query(search_box)
        if len(candidates) == 0:
            return (lon, lat), False

        best_pt = None
        min_dist = float("inf")

        for idx in candidates:
            geom = self.geometries[idx]
            nearest_water_pt, _ = nearest_points(geom, pt)
            d = pt.distance(nearest_water_pt)
            if d < min_dist:
                min_dist = d
                best_pt = (nearest_water_pt.x, nearest_water_pt.y)

        if best_pt is not None and min_dist <= max_radius_deg:
            # Vector from land point to nearest water point
            dx = best_pt[0] - lon
            dy = best_pt[1] - lat
            norm = math.hypot(dx, dy)

            # Try nudging further in the direction of water
            if norm > 1e-7:
                ux = dx / norm
                uy = dy / norm
                for step in [0.015, 0.02, 0.01, 0.005]:
                    nudged = (best_pt[0] + ux * step, best_pt[1] + uy * step)
                    if self.is_point_in_water(nudged[0], nudged[1]):
                        return (round(nudged[0], 5), round(nudged[1], 5)), True

            # Fallback search directions
            for step in [0.01, 0.02, 0.005]:
                for d_x, d_y in [(0, step), (0, -step), (step, 0), (-step, 0),
                                (step, step), (-step, -step), (step, -step), (-step, step)]:
                    test_coord = (round(best_pt[0] + d_x, 5), round(best_pt[1] + d_y, 5))
                    if self.is_point_in_water(test_coord[0], test_coord[1]):
                        return test_coord, True

            return (round(best_pt[0], 5), round(best_pt[1], 5)), True

        return (lon, lat), False


# Singleton instance
spatial_index = SpatialIndex()
