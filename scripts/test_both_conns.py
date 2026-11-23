from app.geo.spatial_index import spatial_index
from app.routing.global_graph import global_graph
from app.routing.local_routing import connect_point_to_graph

G = global_graph.graph

orig = (72.85, 18.95)
dest = (29.90, 31.20)

snapped_orig, ok1 = spatial_index.snap_to_water(orig[0], orig[1])
snapped_dest, ok2 = spatial_index.snap_to_water(dest[0], dest[1])

print(f"Orig: {orig} -> {snapped_orig}, ok={ok1}")
print(f"Dest: {dest} -> {snapped_dest}, ok={ok2}")

p_orig, conns1 = connect_point_to_graph(G, snapped_orig)
print(f"p_orig: {p_orig}, conns: {conns1}")

p_dest, conns2 = connect_point_to_graph(G, snapped_dest)
print(f"p_dest: {p_dest}, conns: {conns2}")
