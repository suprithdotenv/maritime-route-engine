from app.geo.spatial_index import spatial_index
from app.geo.geometry import geodesic_distance_km

# Red Sea navigation channel connecting Gulf of Suez to Bab-el-Mandeb
red_sea_channel = [
    (32.53, 29.50),  # Suez south exit
    (33.80, 27.80),  # Straits of Gubal / entrance to Red Sea
    (35.00, 26.50),  # Northern Red Sea
    (36.50, 24.50),  # Central-North Red Sea
    (38.00, 22.00),  # Central Red Sea (off Jeddah)
    (39.50, 19.50),  # Central-South Red Sea
    (41.00, 16.50),  # Southern Red Sea (Farasan)
    (42.50, 13.80),  # Bab el Mandeb north approach
]

print("=== Validating Red Sea channel ===")
all_ok = True
for idx, pt in enumerate(red_sea_channel):
    w = spatial_index.is_point_in_water(pt[0], pt[1])
    print(f"Pt {idx} {pt}: in_water={w}")
    if not w: all_ok = False

for i in range(len(red_sea_channel) - 1):
    p1 = red_sea_channel[i]
    p2 = red_sea_channel[i+1]
    v = spatial_index.is_edge_valid(p1, p2, max_step_km=20.0)
    print(f"Edge {p1} -> {p2}: valid={v}")
    if not v: all_ok = False

print("All Red Sea edges valid?", all_ok)

# Mediterranean Alboran connector to Gibraltar
alboran_channel = [
    (-4.50, 36.20),  # Gibraltar East exit
    (-2.00, 36.20),  # Alboran Sea Central
    (1.50, 36.80),   # Western Mediterranean (off Algeria/Spain)
    (5.00, 37.50),   # Balearic / Algerian Basin
    (8.50, 38.00),   # South of Sardinia
    (12.50, 37.50),  # Strait of Sicily
]

print("\n=== Validating Alboran / Western Med channel ===")
all_med_ok = True
for idx, pt in enumerate(alboran_channel):
    w = spatial_index.is_point_in_water(pt[0], pt[1])
    print(f"Med Pt {idx} {pt}: in_water={w}")
    if not w: all_med_ok = False

for i in range(len(alboran_channel) - 1):
    p1 = alboran_channel[i]
    p2 = alboran_channel[i+1]
    v = spatial_index.is_edge_valid(p1, p2, max_step_km=20.0)
    print(f"Med Edge {p1} -> {p2}: valid={v}")
    if not v: all_med_ok = False

print("All Med edges valid?", all_med_ok)
