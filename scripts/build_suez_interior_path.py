import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]

# Sample grid points strictly inside poly_1935
print("Sampling grid inside poly 1935...")
poly_prep = poly_1935.buffer(-1e-5) # slight inset to guarantee interior
minx, miny, maxx, maxy = poly_1935.bounds
lons = np.arange(32.25, 32.60, 0.003)
lats = np.arange(30.00, 31.00, 0.003)

points = []
for y in lats:
    for x in lons:
        p = Point(x, y)
        if poly_1935.contains(p):
            points.append((round(x, 5), round(y, 5)))

print(f"Sampled {len(points)} interior points")

# Build local visibility/neighbor graph
G = nx.Graph()
for p in points:
    G.add_node(p)

from shapely.strtree import STRtree
tree_pts = STRtree([Point(p) for p in points])

# Connect each point to nearby points if edge is inside poly_1935
print("Connecting interior graph edges...")
for i, p in enumerate(points):
    pt = Point(p)
    # search neighbors within ~0.008 deg (~800m)
    cands = tree_pts.query(pt.buffer(0.006))
    for c in cands:
        if c > i:
            p2 = points[c]
            line = LineString([p, p2])
            if poly_1935.contains(line):
                G.add_edge(p, p2, weight=pt.distance(Point(p2)))

print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

# Find northernmost and southernmost connected nodes
comps = list(nx.connected_components(G))
print(f"Connected components: {len(comps)}")
largest = max(comps, key=len)
print(f"Largest component size: {len(largest)}")

nodes_in_largest = list(largest)
north_node = max(nodes_in_largest, key=lambda p: p[1])
south_node = min(nodes_in_largest, key=lambda p: p[1])
print(f"North node: {north_node}, South node: {south_node}")

path = nx.shortest_path(G, south_node, north_node, weight='weight')
print(f"Found continuous 100% water path through Suez with {len(path)} waypoints!")
print("Path sample:", path[:3], "...", path[-3:])
