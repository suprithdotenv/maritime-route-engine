import geopandas as gpd
from shapely.geometry import box

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values
from shapely.strtree import STRtree
tree = STRtree(geoms)

panama_box = box(-80.1, 8.8, -79.5, 9.4)
candidates = tree.query(panama_box)
for c in candidates:
    g = geoms[c]
    if g.intersects(panama_box):
        clipped = g.intersection(panama_box)
        print(f"Polygon index {c}: bounds = {[round(x, 4) for x in g.bounds]}, clipped bounds = {[round(x, 4) for x in clipped.bounds]}, type={g.geom_type}", flush=True)

# Check if any Caribbean polygon touches any Pacific polygon
carib = [geoms[c] for c in candidates if geoms[c].intersects(box(-80.1, 9.2, -79.7, 9.4))]
pacific = [geoms[c] for c in candidates if geoms[c].intersects(box(-79.7, 8.8, -79.4, 9.0))]

print(f"Carib count: {len(carib)}, Pacific count: {len(pacific)}", flush=True)
min_gap = min(c.distance(p) for c in carib for p in pacific)
print(f"Min gap between Caribbean and Pacific water polygons: {min_gap:.6f} degrees ({min_gap * 111:.2f} km)", flush=True)
