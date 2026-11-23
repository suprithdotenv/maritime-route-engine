import geopandas as gpd
from shapely.geometry import LineString, Point

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_3253 = gdf.geometry.iloc[3253]

for lat in [31.02, 31.05, 31.10, 31.15, 31.20, 31.25, 31.30]:
    h_line = LineString([(32.0, lat), (33.0, lat)])
    inter = poly_3253.intersection(h_line)
    print(f"Lat {lat:.2f}: {inter.geom_type}, bounds={[round(x, 4) for x in inter.bounds]}")
