import math
from typing import List, Tuple
from pyproj import Geod
from shapely.geometry import LineString, Polygon, MultiPolygon

_GEOD = Geod(ellps="WGS84")


def geodesic_distance_km(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate the geodesic (great-circle) distance in kilometres between two (lon, lat) points.

    Uses the WGS84 reference ellipsoid.
    """
    lon1, lat1 = p1
    lon2, lat2 = p2
    if abs(lon1 - lon2) < 1e-9 and abs(lat1 - lat2) < 1e-9:
        return 0.0
    _, _, distance_m = _GEOD.inv(lon1, lat1, lon2, lat2)
    return distance_m / 1000.0


def interpolate_geodesic(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    max_step_km: float = 20.0
) -> List[Tuple[float, float]]:
    """Interpolate intermediate coordinates along the geodesic path between p1 and p2.

    Returns an ordered list of points including p1 and p2.
    """
    lon1, lat1 = p1
    lon2, lat2 = p2
    total_dist_km = geodesic_distance_km(p1, p2)

    if total_dist_km <= max_step_km or total_dist_km < 1e-3:
        return [p1, p2]

    num_intervals = math.ceil(total_dist_km / max_step_km)
    npts = num_intervals - 1

    try:
        pts = _GEOD.npts(lon1, lat1, lon2, lat2, npts)
        result = [p1] + pts + [p2]
    except Exception:
        # Fallback to linear interpolation in lon/lat if Geod fails
        result = [p1]
        for i in range(1, num_intervals):
            frac = i / num_intervals
            result.append((lon1 + frac * (lon2 - lon1), lat1 + frac * (lat2 - lat1)))
        result.append(p2)

    return result


def route_total_distance_km(coords: List[Tuple[float, float]]) -> float:
    """Calculate the cumulative geodesic distance in kilometres along an ordered sequence of coordinates."""
    if len(coords) < 2:
        return 0.0
    total = 0.0
    for i in range(len(coords) - 1):
        total += geodesic_distance_km(coords[i], coords[i + 1])
    return total


def create_corridor_polygon(
    route_coords: List[Tuple[float, float]],
    buffer_km: float = 150.0
) -> Polygon:
    """Create a corridor polygon surrounding the route coordinates buffered by buffer_km.

    Buffer distance is converted to degrees (~111 km/deg).
    """
    if len(route_coords) == 1:
        p = route_coords[0]
        line = LineString([p, p])
    else:
        line = LineString(route_coords)

    buffer_deg = buffer_km / 111.0
    # Buffer the line
    corridor = line.buffer(buffer_deg, cap_style=1, join_style=1)
    return corridor
