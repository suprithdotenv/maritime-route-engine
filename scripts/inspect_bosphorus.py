import geopandas as gpd
from shapely.geometry import box

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values
from shapely.strtree import STRtree
tree = STRtree(geoms)

bosphorus_box = box(28.9, 40.95, 29.2, 41.3)
candidates = tree.query(bosphorus_box)
print(f"Bosphorus matching count: {len(candidates)}")
for c in candidates:
    g = geoms[c]
    if g.intersects(bosphorus_box):
        clipped = g.intersection(bosphorus_box)
        print(f"Polygon index {c}: bounds={[round(x, 4) for x in g.bounds]}, clipped bounds={[round(x, 4) for x in clipped.bounds]}", flush=True)

marmara = [geoms[c] for c in candidates if geoms[c].intersects(box(28.9, 40.95, 29.1, 41.05))]
black_sea = [geoms[c] for c in candidates if geoms[c].intersects(box(29.0, 41.2, 29.2, 41.3))]
print(f"Marmara count: {len(marmara)}, Black sea count: {len(black_sea)}")
if marmara and black_sea:
    min_gap = min(m.distance(b) for m in marmara for b in black_sea)
    print(f"Min gap between Sea of Marmara and Black Sea: {min_gap:.6f} degrees ({min_gap*111:.3f} km)")
