import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_3253 = gdf.geometry.iloc[3253]
poly_6467 = gdf.geometry.iloc[6467]

# 1. Path inside 3253: from (32.3115, 31.000) to (32.30, 31.35)
print("Finding path inside 3253 (North)...")
north_pts = [(32.300, 31.350), (32.300, 31.300)]
# Let's sample inside 3253 between lat 31.00 and 31.30
lons_n = np.arange(32.28, 32.34, 0.003)
lats_n = np.arange(31.00, 31.30, 0.003)
pts_3253 = []
for y in lats_n:
    for x in lons_n:
        p = Point(x, y)
        if poly_3253.contains(p):
            pts_3253.append((round(float(x), 5), round(float(y), 5)))

Gn = nx.Graph()
for p in pts_3253:
    Gn.add_node(p)
from shapely.strtree import STRtree
tree_n = STRtree([Point(p) for p in pts_3253])
for i, p in enumerate(pts_3253):
    pt = Point(p)
    cands = tree_n.query(pt.buffer(0.006))
    for c in cands:
        if c > i:
            p2 = pts_3253[c]
            line = LineString([p, p2])
            if poly_3253.contains(line):
                Gn.add_edge(p, p2, weight=pt.distance(Point(p2)))

comp_n = max(nx.connected_components(Gn), key=len)
sub_n = Gn.subgraph(comp_n)
start_n = min(comp_n, key=lambda p: p[1])
end_n = max(comp_n, key=lambda p: p[1])
path_north = nx.shortest_path(sub_n, start_n, end_n, weight='weight')
print(f"Path north has {len(path_north)} points: {path_north[0]} to {path_north[-1]}")

# 2. Path inside 6467: from (32.5828, 30.000) to (32.65, 29.50)
print("Finding path inside 6467 (South)...")
lons_s = np.arange(32.50, 32.66, 0.005)
lats_s = np.arange(29.50, 30.005, 0.005)
pts_6467 = []
for y in lats_s:
    for x in lons_s:
        p = Point(x, y)
        if poly_6467.contains(p):
            pts_6467.append((round(float(x), 5), round(float(y), 5)))

Gs = nx.Graph()
for p in pts_6467:
    Gs.add_node(p)
tree_s = STRtree([Point(p) for p in pts_6467])
for i, p in enumerate(pts_6467):
    pt = Point(p)
    cands = tree_s.query(pt.buffer(0.01))
    for c in cands:
        if c > i:
            p2 = pts_6467[c]
            line = LineString([p, p2])
            if poly_6467.contains(line):
                Gs.add_edge(p, p2, weight=pt.distance(Point(p2)))

comp_s = max(nx.connected_components(Gs), key=len)
sub_s = Gs.subgraph(comp_s)
start_s = max(comp_s, key=lambda p: p[1])
end_s = min(comp_s, key=lambda p: p[1])
path_south = nx.shortest_path(sub_s, start_s, end_s, weight='weight')
print(f"Path south has {len(path_south)} points: {path_south[0]} to {path_south[-1]}")
