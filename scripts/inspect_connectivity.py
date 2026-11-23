import geopandas as gpd
from shapely.geometry import box, LineString, Point
from shapely.ops import unary_union

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values

from shapely.strtree import STRtree
tree = STRtree(geoms)

def inspect_corridor(name, bbox, start_pt, end_pt):
    print(f"\n================ {name} ================")
    b_box = box(*bbox)
    candidates = tree.query(b_box)
    local_geoms = [geoms[c] for c in candidates if geoms[c].intersects(b_box)]
    print(f"Total matching water polygons in corridor: {len(local_geoms)}")
    
    # Clip to bbox
    clipped = [g.intersection(b_box) for g in local_geoms]
    union_water = unary_union(clipped)
    print(f"Union water type: {union_water.geom_type}")
    
    p_start = Point(*start_pt)
    p_end = Point(*end_pt)
    print(f"Start {start_pt} in water: {union_water.contains(p_start)}")
    print(f"End {end_pt} in water: {union_water.contains(p_end)}")
    
    # Check if start and end are in the same connected component
    if union_water.geom_type == 'MultiPolygon':
        print(f"Number of disconnected water parts in {name} bbox: {len(union_water.geoms)}")
        start_part = [i for i, p in enumerate(union_water.geoms) if p.contains(p_start) or p.distance(p_start) < 0.005]
        end_part = [i for i, p in enumerate(union_water.geoms) if p.contains(p_end) or p.distance(p_end) < 0.005]
        print(f"Start in part: {start_part}, End in part: {end_part}")
        if start_part and end_part and start_part[0] == end_part[0]:
            print(">>> CONNECTED IN GEOMETRY! Continuous water passage exists!")
        else:
            print(">>> Disconnected or separated parts. Let's inspect gap distances.")
            # find min distance between parts
            for i, p1 in enumerate(union_water.geoms):
                for j, p2 in enumerate(union_water.geoms):
                    if i < j:
                        d = p1.distance(p2)
                        print(f"  Distance between part {i} and part {j}: {d:.6f} degrees (~{d*111:.3f} km)")
    elif union_water.geom_type == 'Polygon':
        print(">>> SINGLE POLYGON: Continuous water passage exists!")

# Suez: Port Said (Mediterranean ~ 32.31, 31.27) to Port Tewfik / Suez (Red Sea ~ 32.56, 29.93)
inspect_corridor('Suez Canal', (32.2, 29.8, 32.65, 31.35), (32.31, 31.27), (32.56, 29.93))

# Panama: Colon / Cristobal (Caribbean ~ -79.91, 9.35) to Balboa / Panama (Pacific ~ -79.56, 8.95)
inspect_corridor('Panama Canal', (-80.05, 8.85, -79.50, 9.40), (-79.91, 9.35), (-79.56, 8.95))

# Hormuz: Persian Gulf (55.0, 26.5) to Gulf of Oman (57.5, 25.5)
inspect_corridor('Strait of Hormuz', (55.0, 25.0, 58.0, 27.5), (55.5, 26.5), (57.0, 25.5))

# Malacca: Andaman Sea (98.0, 5.0) to Singapore (104.0, 1.2)
inspect_corridor('Strait of Malacca', (98.0, 1.0, 104.5, 6.0), (99.0, 4.0), (103.5, 1.3))
