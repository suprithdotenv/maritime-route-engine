import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values
tree = STRtree(geoms)

def is_water(lon, lat):
    pt = Point(lon, lat)
    cands = tree.query(pt)
    return any(geoms[c].contains(pt) for c in cands)

def is_edge_valid(p1, p2, step_deg=0.005):
    dist = Point(p1).distance(Point(p2))
    num_pts = max(3, int(dist / step_deg))
    for frac in np.linspace(0, 1, num_pts):
        lon = p1[0] + frac * (p2[0] - p1[0])
        lat = p1[1] + frac * (p2[1] - p1[1])
        if not is_water(lon, lat):
            return False
    return True

# 1. Singapore Strait adjustment
p_west = (103.50, 1.25)
p_east = (104.30, 1.30)
for lat in np.linspace(1.10, 1.25, 16):
    for lon in np.linspace(103.75, 103.95, 21):
        if is_water(lon, lat) and is_edge_valid(p_west, (lon, lat), 0.01) and is_edge_valid((lon, lat), p_east, 0.01):
            print(f"Found valid Singapore midpoint: ({lon:.4f}, {lat:.4f})")
            break

# 2. Extract smooth Suez path:
# Let's find polygon 1935, 3253, 6467
poly_1935 = gdf.geometry.iloc[1935]
poly_3253 = gdf.geometry.iloc[3253]
poly_6467 = gdf.geometry.iloc[6467]

# In 1935, let's take dense lat slices
suez_pts = []
# From North: 31.4 to 31.0 in poly 3253
for lat in [31.40, 31.35, 31.30, 31.25, 31.20, 31.15, 31.10, 31.05, 31.00]:
    h_line = LineString([(32.2, lat), (32.4, lat)])
    inter = poly_3253.intersection(h_line)
    if not inter.is_empty:
        # take the piece nearest to lon 32.31
        if inter.geom_type == 'MultiLineString':
            lines = [l for l in inter.geoms]
            best_line = min(lines, key=lambda l: abs((l.coords[0][0] + l.coords[-1][0])/2 - 32.31))
            mid_lon = (best_line.coords[0][0] + best_line.coords[-1][0]) / 2
        else:
            mid_lon = (inter.coords[0][0] + inter.coords[-1][0]) / 2
        suez_pts.append((round(mid_lon, 5), round(lat, 5)))

# In 1935: lat 30.98 to 30.02
for lat in np.linspace(30.98, 30.02, 50):
    h_line = LineString([(32.2, lat), (32.6, lat)])
    inter = poly_1935.intersection(h_line)
    if not inter.is_empty:
        if inter.geom_type == 'MultiLineString':
            # take longest line or nearest to previous
            lines = [l for l in inter.geoms]
            prev_lon = suez_pts[-1][0] if suez_pts else 32.31
            best_line = min(lines, key=lambda l: abs((l.coords[0][0] + l.coords[-1][0])/2 - prev_lon))
            mid_lon = (best_line.coords[0][0] + best_line.coords[-1][0]) / 2
        else:
            mid_lon = (inter.coords[0][0] + inter.coords[-1][0]) / 2
        suez_pts.append((round(mid_lon, 5), round(lat, 5)))

# In 6467: lat 29.98 to 29.50
for lat in [29.98, 29.95, 29.90, 29.80, 29.50]:
    h_line = LineString([(32.4, lat), (32.7, lat)])
    inter = poly_6467.intersection(h_line)
    if not inter.is_empty:
        mid_lon = (inter.bounds[0] + inter.bounds[2]) / 2
        suez_pts.append((round(mid_lon, 5), round(lat, 5)))

print(f"\nGenerated {len(suez_pts)} raw Suez points. Testing validity...")
valid_pts = []
for p in suez_pts:
    if is_water(p[0], p[1]):
        valid_pts.append(p)
print(f"Valid points in water: {len(valid_pts)} / {len(suez_pts)}")

# Now check edges
valid_edges = 0
invalid_edges = 0
for i in range(len(valid_pts) - 1):
    if is_edge_valid(valid_pts[i], valid_pts[i+1], 0.002):
        valid_edges += 1
    else:
        invalid_edges += 1
        print(f"Edge {i} invalid: {valid_pts[i]} -> {valid_pts[i+1]}")
print(f"Valid edges: {valid_edges}, Invalid: {invalid_edges}")
