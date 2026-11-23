import time
import sys
import psutil
import pyogrio
import geopandas as gpd
from shapely.strtree import STRtree
from shapely.geometry import Point

shp_path = 'data/water-polygons-split-4326/water_polygons.shp'

print(f"Memory before: {psutil.Process().memory_info().rss / 1024**2:.1f} MB", flush=True)

t0 = time.time()
print("Reading geometries with pyogrio (geometry only)...", flush=True)
# read_dataframe with columns=[] only loads the geometry column, saving RAM and time
gdf = pyogrio.read_dataframe(shp_path, columns=[])
t_read = time.time() - t0
print(f"Read {len(gdf)} geometries in {t_read:.2f}s", flush=True)
print(f"Memory after read: {psutil.Process().memory_info().rss / 1024**2:.1f} MB", flush=True)

geoms = gdf.geometry.values

t0 = time.time()
print("Building STRtree...", flush=True)
tree = STRtree(geoms)
t_tree = time.time() - t0
print(f"Built STRtree in {t_tree:.2f}s", flush=True)
print(f"Memory after STRtree: {psutil.Process().memory_info().rss / 1024**2:.1f} MB", flush=True)

test_points = {
    'Atlantic (0, 0)': (0.0, 0.0),
    'Pacific (-170, 0)': (-170.0, 0.0),
    'Indian Ocean (70, 0)': (70.0, 0.0),
    'Sahara Desert (20, 20)': (20.0, 20.0),
    'Central Europe (10, 50)': (10.0, 50.0),
    'Mumbai Port water (72.85, 18.95)': (72.85, 18.95),
    'Alexandria Port water (29.9, 31.2)': (29.9, 31.2),
    'Red Sea (38, 20)': (38.0, 20.0),
    'Suez Canal (32.33, 30.5)': (32.33, 30.5),
    'Strait of Hormuz (56.5, 26.5)': (56.5, 26.5),
    'Strait of Malacca (101.5, 2.5)': (101.5, 2.5),
    'Panama Canal (-79.9, 9.1)': (-79.9, 9.1),
}

for name, (lon, lat) in test_points.items():
    pt = Point(lon, lat)
    t0 = time.time()
    candidates = tree.query(pt)
    inside = any(geoms[c].contains(pt) for c in candidates)
    t_query = (time.time() - t0) * 1000
    print(f"{name}: inside={inside} (candidates: {len(candidates)}, took {t_query:.3f}ms)", flush=True)
