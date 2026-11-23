import geopandas as gpd
from shapely.geometry import LineString, Point

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]

print("Exterior coords count:", len(poly_1935.exterior.coords))
# Let's inspect some sample coordinates along the canal
coords = list(poly_1935.exterior.coords)
# Sort by latitude
sorted_by_lat = sorted(coords, key=lambda c: c[1])
print("Lowest lat in 1935:", sorted_by_lat[0], "Highest lat:", sorted_by_lat[-1])

# Check how wide the polygon is across latitudes
import numpy as np
for lat in [30.05, 30.2, 30.4, 30.6, 30.8, 30.95]:
    h_line = LineString([(32.0, lat), (33.0, lat)])
    inter = poly_1935.intersection(h_line)
    print(f"Lat {lat:.2f}: {inter.geom_type}, bounds={[round(x, 4) for x in inter.bounds]}")
