import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
import numpy as np
from app.geo.spatial_index import spatial_index

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_3253 = gdf.geometry.iloc[3253]
poly_6467 = gdf.geometry.iloc[6467]

# 1. North in 3253:
pts_3253 = []
for y in np.arange(31.00, 31.30, 0.003):
    for x in np.arange(32.28, 32.34, 0.003):
        p = Point(x, y)
        if poly_3253.contains(p):
            pts_3253.append((round(float(x), 5), round(float(y), 5)))

Gn = nx.Graph()
for p in pts_3253: Gn.add_node(p)
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
path_north = nx.shortest_path(sub_n, end_n, start_n, weight='weight') # from North (31.30) down to 31.00

# 2. Central in 1935:
pts_1935 = []
for y in np.arange(30.00, 31.00, 0.003):
    for x in np.arange(32.25, 32.60, 0.003):
        p = Point(x, y)
        if poly_1935.contains(p):
            pts_1935.append((round(float(x), 5), round(float(y), 5)))

Gc = nx.Graph()
for p in pts_1935: Gc.add_node(p)
tree_c = STRtree([Point(p) for p in pts_1935])
for i, p in enumerate(pts_1935):
    pt = Point(p)
    cands = tree_c.query(pt.buffer(0.006))
    for c in cands:
        if c > i:
            p2 = pts_1935[c]
            line = LineString([p, p2])
            if poly_1935.contains(line):
                Gc.add_edge(p, p2, weight=pt.distance(Point(p2)))

comp_c = max(nx.connected_components(Gc), key=len)
sub_c = Gc.subgraph(comp_c)
start_c = max(comp_c, key=lambda p: p[1])
end_c = min(comp_c, key=lambda p: p[1])
path_central = nx.shortest_path(sub_c, start_c, end_c, weight='weight') # from 31.00 down to 30.00

# 3. South in 6467:
pts_6467 = []
for y in np.arange(29.50, 30.005, 0.005):
    for x in np.arange(32.50, 32.66, 0.005):
        p = Point(x, y)
        if poly_6467.contains(p):
            pts_6467.append((round(float(x), 5), round(float(y), 5)))

Gs = nx.Graph()
for p in pts_6467: Gs.add_node(p)
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
path_south = nx.shortest_path(sub_s, start_s, end_s, weight='weight') # from 30.00 down to 29.50

# Full raw path
raw_full = path_north + path_central + path_south

# Simplify raw_full using spatial_index.is_edge_valid
print(f"Total raw points: {len(raw_full)}. Simplifying with spatial_index.is_edge_valid...")
simplified = [raw_full[0]]
curr = 0
while curr < len(raw_full) - 1:
    next_idx = curr + 1
    # look ahead up to 25 steps to save time
    max_lookahead = min(len(raw_full) - 1, curr + 25)
    for candidate in range(max_lookahead, curr, -1):
        if spatial_index.is_edge_valid(raw_full[curr], raw_full[candidate], max_step_km=5.0):
            next_idx = candidate
            break
    simplified.append(raw_full[next_idx])
    curr = next_idx

print(f"\nFinal optimal Suez Canal corridor ({len(simplified)} waypoints):")
for pt in simplified:
    print(f"    ({pt[0]}, {pt[1]}),")

# Validate all consecutive edges
all_ok = True
for i in range(len(simplified) - 1):
    if not spatial_index.is_edge_valid(simplified[i], simplified[i+1], max_step_km=5.0):
        print(f"Edge {i} invalid: {simplified[i]} -> {simplified[i+1]}")
        all_ok = False

print("\n>>> All Suez edges 100% strictly in water?", all_ok)
