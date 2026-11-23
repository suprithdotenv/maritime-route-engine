import geopandas as gpd

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_3253 = gdf.geometry.iloc[3253]

inter_north = poly_1935.intersection(poly_3253)
print(f"Intersection between 1935 and 3253: {inter_north.geom_type}, bounds={inter_north.bounds}")
