from app.geo.spatial_index import spatial_index
from shapely.geometry import Point

dest = (29.90, 31.20)
# Nearest water point
pt = Point(dest)
cands = spatial_index.tree.query(pt.buffer(0.5))
for c in cands:
    g = spatial_index.geometries[c]
    from shapely.ops import nearest_points
    np_pt, _ = nearest_points(g, pt)
    print(f"Cand {c} nearest point: ({np_pt.x:.6f}, {np_pt.y:.6f})")
    # If we move 0.01 deg north into Mediterranean:
    test_pt = (np_pt.x, np_pt.y + 0.02)
    print(f"  test pt (+0.02 lat): {test_pt}, in_water={spatial_index.is_point_in_water(test_pt[0], test_pt[1])}")
