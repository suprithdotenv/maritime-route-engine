import pickle
import networkx as nx

with open("data/cache/global_graph.pickle", "rb") as f:
    G = pickle.load(f)

# Find Suez nodes
suez_nodes = [n for n in G.nodes if G.nodes[n].get("chokepoint") == "suez_canal"]
print(f"Suez nodes in graph: {len(suez_nodes)}")
print("Suez north endpoint:", suez_nodes[0], "Neighbors:", list(G.neighbors(suez_nodes[0])))
print("Suez south endpoint:", suez_nodes[-1], "Neighbors:", list(G.neighbors(suez_nodes[-1])))

# Check which components they belong to
comps = list(nx.connected_components(G))
for i, comp in enumerate(comps):
    suez_in_comp = [n for n in suez_nodes if n in comp]
    if suez_in_comp:
        print(f"Component {i} has {len(comp)} nodes and {len(suez_in_comp)} Suez nodes")

# Check Mediterranean nodes: e.g. lon between 10 and 35, lat between 32 and 40
med_nodes = [n for n in G.nodes if 10.0 <= n[0] <= 35.0 and 32.0 <= n[1] <= 42.0]
print(f"Mediterranean nodes count: {len(med_nodes)}")
for m in med_nodes[:5]:
    comp_id = [i for i, c in enumerate(comps) if m in c][0]
    print(f"Med node {m} in component {comp_id}")
