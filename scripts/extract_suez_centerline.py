import geopandas as gpd
from shapely.geometry import LineString, Point
import numpy as np

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_3253 = gdf.geometry.iloc[3253]
poly_6467 = gdf.geometry.iloc[6467]

centerline = []
# Slicing from lat 30.00 to 31.00
for lat in np.linspace(30.01, 30.99, 25):
    h_line = LineString([(32.0, lat), (33.0, lat)])
    inter = poly_1935.intersection(h_line)
    if not inter.is_empty:
        if inter.geom_type == 'LineString':
            mid_x = (inter.coords[0][0] + inter.coords[-1][0]) / 2.0
            centerline.append((round(mid_x, 5), round(lat, 5)))
        elif inter.geom_type == 'MultiLineString':
            # take longest
            longest = max(inter.geoms, key=lambda l: l.length)
            mid_x = (longest.coords[0][0] + longest.coords[-1][0]) / 2.0
            centerline.append((round(mid_x, 5), round(lat, 5)))

print(f"Extracted {len(centerline)} centerline points for Suez Canal:")
for pt in centerline:
    print(f"  {pt},")

# Check connectivity between consecutive points
all_ok = True
for i in range(len(centerline) - 1):
    p1 = centerline[i]
    p2 = centerline[i+1]
    seg = LineString([p1, p2])
    # check if seg is inside 1935
    in_water = poly_1935.contains(seg) or poly_1935.covers(seg) or poly_1935.buffer(1e-4).contains(seg)
    if not in_water:
        all_ok = False
        print(f"  Gap between {p1} and {p2}")

print("All consecutive segments in water?", all_ok)
