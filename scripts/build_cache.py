import time
import os
import pyogrio
import geopandas as gpd
from shapely.geometry import box, Point

shp_path = 'data/water-polygons-split-4326/water_polygons.shp'
cache_dir = 'data/cache'
parquet_path = os.path.join(cache_dir, 'water_polygons.parquet')

os.makedirs(cache_dir, exist_ok=True)

if not os.path.exists(parquet_path):
    print("Reading shapefile with pyogrio (geometry only)...", flush=True)
    t0 = time.time()
    gdf = pyogrio.read_dataframe(shp_path, columns=[])
    print(f"Read shapefile in {time.time()-t0:.2f}s, saving to {parquet_path}...", flush=True)
    t0 = time.time()
    gdf.to_parquet(parquet_path)
    print(f"Saved parquet in {time.time()-t0:.2f}s", flush=True)
else:
    print(f"Parquet cache {parquet_path} already exists.", flush=True)

print("Testing fast read from parquet...", flush=True)
t0 = time.time()
gdf = gpd.read_parquet(parquet_path)
print(f"Loaded {len(gdf)} records from parquet in {time.time()-t0:.2f}s!", flush=True)

straits = {
    'Suez Canal': (32.2, 29.8, 32.6, 31.4), # minx, miny, maxx, maxy
    'Panama Canal': (-80.1, 8.8, -79.5, 9.4),
    'Strait of Hormuz': (56.0, 26.0, 57.0, 27.0),
    'Strait of Malacca': (101.0, 1.5, 104.0, 3.5),
    'Bab el Mandeb': (43.0, 12.4, 43.6, 13.0),
    'Strait of Gibraltar': (-6.0, 35.8, -5.2, 36.2),
    'English Channel': (1.0, 50.8, 1.8, 51.2),
    'Bosphorus': (28.9, 41.0, 29.2, 41.3)
}

from shapely.strtree import STRtree
geoms = gdf.geometry.values
print("Building STRtree...", flush=True)
t0 = time.time()
tree = STRtree(geoms)
print(f"Built STRtree in {time.time()-t0:.2f}s", flush=True)

for name, bbox in straits.items():
    b_geom = box(*bbox)
    t0 = time.time()
    candidates = tree.query(b_geom)
    matching_geoms = [geoms[c] for c in candidates if geoms[c].intersects(b_geom)]
    print(f"\n=== {name} (bbox: {bbox}) ===")
    print(f"Found {len(matching_geoms)} intersecting water polygons in {(time.time()-t0)*1000:.2f}ms")
    if matching_geoms:
        total_intersecting_area = sum(g.intersection(b_geom).area for g in matching_geoms)
        print(f"Water area in bbox: {total_intersecting_area:.4f} (BBox area: {b_geom.area:.4f})")
