from app.geo.spatial_index import spatial_index
from app.routing.global_graph import global_graph
from app.routing.local_routing import connect_point_to_graph
from app.geo.geometry import geodesic_distance_km

dest = (29.90, 31.20)
snapped, ok = spatial_index.snap_to_water(dest[0], dest[1])
print(f"Alexandria {dest} snapped to {snapped}, ok={ok}")

G = global_graph.graph
all_nodes = list(G.nodes)
# nearest 10 nodes to snapped
sorted_nodes = sorted(all_nodes, key=lambda n: geodesic_distance_km(snapped, n))[:10]
for n in sorted_nodes:
    d = geodesic_distance_km(snapped, n)
    v = spatial_index.is_edge_valid(snapped, n, max_step_km=15.0)
    print(f"Node {n}: dist={d:.1f} km, valid={v}, type={G.nodes[n].get('node_type')}")
