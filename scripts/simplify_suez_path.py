import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]

lons = np.arange(32.25, 32.60, 0.003)
lats = np.arange(30.00, 31.00, 0.003)

points = []
for y in lats:
    for x in lons:
        p = Point(x, y)
        if poly_1935.contains(p):
            points.append((round(float(x), 5), round(float(y), 5)))

G = nx.Graph()
for p in points:
    G.add_node(p)

from shapely.strtree import STRtree
tree_pts = STRtree([Point(p) for p in points])

for i, p in enumerate(points):
    pt = Point(p)
    cands = tree_pts.query(pt.buffer(0.006))
    for c in cands:
        if c > i:
            p2 = points[c]
            line = LineString([p, p2])
            if poly_1935.contains(line):
                G.add_edge(p, p2, weight=pt.distance(Point(p2)))

comps = list(nx.connected_components(G))
largest = max(comps, key=len)
nodes_in_largest = list(largest)
north_node = max(nodes_in_largest, key=lambda p: p[1])
south_node = min(nodes_in_largest, key=lambda p: p[1])

path = nx.shortest_path(G, south_node, north_node, weight='weight')

# Shortcut the path: greedily advance as far as line stays in water
simplified = [path[0]]
curr = 0
while curr < len(path) - 1:
    next_idx = curr + 1
    for candidate in range(len(path) - 1, curr, -1):
        test_line = LineString([path[curr], path[candidate]])
        if poly_1935.contains(test_line):
            next_idx = candidate
            break
    simplified.append(path[next_idx])
    curr = next_idx

print(f"Simplified 178 waypoints down to {len(simplified)} optimal waypoints:")
for pt in simplified:
    print(f"    ({pt[0]}, {pt[1]}),")
