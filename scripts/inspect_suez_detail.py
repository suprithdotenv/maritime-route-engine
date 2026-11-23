import geopandas as gpd
from shapely.geometry import box, Point

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
geoms = gdf.geometry.values
from shapely.strtree import STRtree
tree = STRtree(geoms)

suez_box = box(32.0, 29.8, 32.7, 31.5)
candidates = tree.query(suez_box)
for c in candidates:
    g = geoms[c]
    if g.intersects(suez_box):
        clipped = g.intersection(suez_box)
        print(f"Polygon index {c}: bounds = {[round(x, 4) for x in g.bounds]}, clipped bounds = {[round(x, 4) for x in clipped.bounds]}, type={g.geom_type}")
