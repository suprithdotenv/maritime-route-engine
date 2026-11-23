from app.routing.chokepoints import get_supported_chokepoints
from app.geo.spatial_index import spatial_index

supported = get_supported_chokepoints()
print(f"Validating {len(supported)} supported chokepoint corridors...")

all_valid = True
for key, chk in supported.items():
    name = chk["name"]
    corridor = chk["corridor"]
    print(f"\n--- {name} ({len(corridor)} waypoints) ---")
    
    # Check all waypoints
    pts_valid = True
    for idx, pt in enumerate(corridor):
        in_water = spatial_index.is_point_in_water(pt[0], pt[1])
        if not in_water:
            pts_valid = False
            all_valid = False
            print(f"  Waypoint {idx} {pt} is NOT in water!")
    
    if pts_valid:
        print(f"  All {len(corridor)} waypoints are strictly in water.")
    
    # Check edges
    edges_valid = True
    for i in range(len(corridor) - 1):
        p1 = corridor[i]
        p2 = corridor[i+1]
        valid_edge = spatial_index.is_edge_valid(p1, p2, max_step_km=10.0)
        if not valid_edge:
            edges_valid = False
            all_valid = False
            print(f"  Edge between {p1} and {p2} is INVALID (crosses land)!")
    
    if edges_valid:
        print(f"  All {len(corridor)-1} consecutive corridor edges are VALID (zero land crossing).")

print(f"\n>>> Overall Chokepoint Validation Passed? {all_valid}")
