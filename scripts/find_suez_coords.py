import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values
tree = STRtree(geoms)

def is_water(lon, lat):
    pt = Point(lon, lat)
    cands = tree.query(pt)
    return any(geoms[c].contains(pt) for c in cands)

# Suez canal waypoints: check each
suez_test = [
    (32.32, 31.40),
    (32.315, 31.27),
    (32.32, 31.00),
    (32.34, 30.50),
    (32.41, 30.34),
    (32.55, 29.98),
    (32.55, 29.80),
]

print("=== Testing Suez test points ===")
for lon, lat in suez_test:
    w = is_water(lon, lat)
    print(f"({lon}, {lat}): {w}")
    if not w:
        # find nearby point in poly 1935 or candidates
        pt = Point(lon, lat)
        cands = tree.query(pt.buffer(0.05))
        for c in cands:
            from shapely.ops import nearest_points
            np_pt, _ = nearest_points(geoms[c], pt)
            print(f"   nearest point in cand {c}: ({np_pt.x:.5f}, {np_pt.y:.5f}), in_water={is_water(np_pt.x, np_pt.y)}")
