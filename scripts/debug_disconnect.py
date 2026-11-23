import pickle
import networkx as nx

with open("data/cache/global_graph.pickle", "rb") as f:
    G = pickle.load(f)

comps = sorted(nx.connected_components(G), key=len, reverse=True)
print(f"Top 5 component sizes: {[len(c) for c in comps[:5]]}")

# Component containing Suez:
comp_suez = [c for c in comps if (32.304, 31.3) in c][0]
print(f"Suez component size: {len(comp_suez)}")
print("Nodes in Suez component:")
for n in sorted(comp_suez, key=lambda x: (x[1], x[0])):
    print(f"  {n}: type={G.nodes[n].get('node_type')}, chk={G.nodes[n].get('chokepoint')}")

# Check Bab el Mandeb:
bam_nodes = [n for n in G.nodes if G.nodes[n].get("chokepoint") == "bab_el_mandeb"]
print("\nBab el Mandeb nodes:")
for n in bam_nodes:
    c_idx = [i for i, c in enumerate(comps) if n in c][0]
    print(f"  {n}: in comp {c_idx}, neighbors: {list(G.neighbors(n))}")

# Check Gibraltar:
gib_nodes = [n for n in G.nodes if G.nodes[n].get("chokepoint") == "strait_of_gibraltar"]
print("\nGibraltar nodes:")
for n in gib_nodes:
    c_idx = [i for i, c in enumerate(comps) if n in c][0]
    print(f"  {n}: in comp {c_idx}, neighbors: {list(G.neighbors(n))}")
