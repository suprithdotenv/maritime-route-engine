import geopandas as gpd
from shapely.geometry import Point, box, LineString
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values

from shapely.strtree import STRtree
tree = STRtree(geoms)

def is_point_in_water(lon, lat):
    pt = Point(lon, lat)
    candidates = tree.query(pt)
    return any(geoms[c].contains(pt) for c in candidates)

print("=== Checking Suez Canal coordinates ===", flush=True)
# Port Said entrance to Mediterranean: lon ~ 32.31, lat ~ 31.27
# Great Bitter Lake: lon ~ 32.38, lat ~ 30.34
# Port Tewfik / Gulf of Suez entrance: lon ~ 32.56, lat ~ 29.93
suez_coords = [
    (32.31, 31.28, "Port Said North Approach"),
    (32.31, 31.25, "Port Said Harbor"),
    (32.32, 31.15, "Suez Canal North"),
    (32.32, 30.95, "El Qantara"),
    (32.33, 30.70, "Ismailia Approach"),
    (32.34, 30.58, "Lake Timsah"),
    (32.38, 30.40, "Great Bitter Lake North"),
    (32.43, 30.30, "Great Bitter Lake South"),
    (32.55, 30.00, "Suez Canal South"),
    (32.56, 29.93, "Port Tewfik / Gulf of Suez")
]

for lon, lat, desc in suez_coords:
    # also check nearby points within 0.01 deg (~1 km)
    in_water = is_point_in_water(lon, lat)
    # search around
    best_dist = 999
    b_cand = tree.query(box(lon-0.05, lat-0.05, lon+0.05, lat+0.05))
    if len(b_cand) > 0:
        local = [geoms[c] for c in b_cand]
        pt = Point(lon, lat)
        dists = [g.distance(pt) for g in local]
        best_dist = min(dists)
    print(f"Suez: {desc} ({lon:.2f}, {lat:.2f}) -> in_water={in_water}, dist_to_water={best_dist*111:.3f} km")

print("\n=== Checking Panama Canal coordinates ===", flush=True)
# Colon / Cristobal: -79.91, 9.35
# Gatun Lake: -79.85, 9.20
# Culebra Cut: -79.65, 9.03
# Balboa: -79.56, 8.95
panama_coords = [
    (-79.91, 9.36, "Colon / Cristobal Caribbean"),
    (-79.92, 9.27, "Gatun Locks"),
    (-79.85, 9.15, "Gatun Lake"),
    (-79.68, 9.05, "Culebra Cut"),
    (-79.59, 8.98, "Miraflores Locks"),
    (-79.56, 8.95, "Balboa / Pacific")
]

for lon, lat, desc in panama_coords:
    in_water = is_point_in_water(lon, lat)
    b_cand = tree.query(box(lon-0.05, lat-0.05, lon+0.05, lat+0.05))
    best_dist = 999
    if len(b_cand) > 0:
        local = [geoms[c] for c in b_cand]
        pt = Point(lon, lat)
        best_dist = min(g.distance(pt) for g in local)
    print(f"Panama: {desc} ({lon:.2f}, {lat:.2f}) -> in_water={in_water}, dist_to_water={best_dist*111:.3f} km")

print("\n=== Checking Bab el Mandeb & Hormuz & Malacca & Gibraltar ===", flush=True)
other_straits = [
    (43.35, 12.60, "Bab el Mandeb"),
    (56.45, 26.35, "Strait of Hormuz"),
    (101.50, 2.50, "Strait of Malacca"),
    (103.80, 1.25, "Singapore Strait"),
    (-5.60, 35.95, "Strait of Gibraltar"),
    (1.40, 51.00, "Strait of Dover"),
    (29.05, 41.10, "Bosphorus"),
    (26.40, 40.20, "Dardanelles")
]

for lon, lat, desc in other_straits:
    in_water = is_point_in_water(lon, lat)
    print(f"{desc} ({lon:.2f}, {lat:.2f}) -> in_water={in_water}")
