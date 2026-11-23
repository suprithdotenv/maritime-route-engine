import geopandas as gpd
from shapely.geometry import Point

parquet_path = 'data/cache/water_polygons.parquet'
gdf = gpd.read_parquet(parquet_path)
poly_1935 = gdf.geometry.iloc[1935]
poly_6467 = gdf.geometry.iloc[6467]
poly_3253 = gdf.geometry.iloc[3253]

print("Polygon 1935 area:", poly_1935.area, "type:", poly_1935.geom_type, flush=True)
print("Does 1935 intersect 6467 (Red Sea)?", poly_1935.intersects(poly_6467), flush=True)
print("Does 1935 intersect 3253 (Mediterranean)?", poly_1935.intersects(poly_3253), flush=True)

if poly_1935.geom_type == 'MultiPolygon':
    print(f"1935 has {len(poly_1935.geoms)} parts", flush=True)
    for i, g in enumerate(poly_1935.geoms):
        print(f"  Part {i}: bounds={[round(x, 4) for x in g.bounds]}, area={g.area:.6f}", flush=True)
elif poly_1935.geom_type == 'Polygon':
    print("1935 is a single Polygon! Bounds:", [round(x, 4) for x in poly_1935.bounds], flush=True)

# Representative point
print("1935 representative point:", poly_1935.representative_point().coords[:], flush=True)
