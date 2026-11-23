import time
from app.routing.global_graph import global_graph

print("Triggering global graph construction and caching...")
t0 = time.time()
G = global_graph.load_or_build()
print(f"Global graph ready in {time.time()-t0:.2f}s!")
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# Check connectivity
import networkx as nx
comps = list(nx.connected_components(G))
print(f"Connected components: {len(comps)}")
largest = max(comps, key=len)
print(f"Largest component has {len(largest)} nodes ({len(largest)/G.number_of_nodes()*100:.1f}% of all nodes)")

# Test test route through Suez
# Mumbai (approx ocean node: 70.0, 18.0) to Mediterranean (approx ocean node: 28.0, 34.0)
from app.geo.geometry import geodesic_distance_km

# Find nearest nodes
mumbai_node = min(largest, key=lambda n: geodesic_distance_km(n, (72.8, 18.9)))
alex_node = min(largest, key=lambda n: geodesic_distance_km(n, (29.9, 31.2)))
print(f"Mumbai node: {mumbai_node}, Mediterranean node: {alex_node}")

try:
    path = nx.shortest_path(G, mumbai_node, alex_node, weight='weight')
    path_len = sum(geodesic_distance_km(path[i], path[i+1]) for i in range(len(path)-1))
    print(f"\nRoute found! {len(path)} waypoints, total distance: {path_len:.1f} km")
    # Check if path uses Suez
    uses_suez = any(G.nodes[n].get("chokepoint") == "suez_canal" for n in path)
    print(f">>> Does the route traverse Suez Canal? {uses_suez}!")
except Exception as e:
    print(f"Error finding test path: {e}")
