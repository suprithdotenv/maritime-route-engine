import geopandas as gpd
from shapely.geometry import Point

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_6467 = gdf.geometry.iloc[6467]

inter = poly_1935.intersection(poly_6467)
print(f"Intersection between 1935 and 6467: {inter.geom_type}, bounds={inter.bounds}")
if inter.geom_type in ['LineString', 'MultiLineString']:
    for p in inter.coords if hasattr(inter, 'coords') else [pt for line in inter.geoms for pt in line.coords]:
        print(f"Touch point: {p}")
