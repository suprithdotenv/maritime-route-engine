import pyogrio
from shapely.geometry import box, MultiPolygon, Polygon
import numpy as np

shp_path = 'data/water-polygons-split-4326/water_polygons.shp'

straits = {
    'Suez Canal': (32.2, 29.8, 32.6, 31.4), # minx, miny, maxx, maxy
    'Panama Canal': (-80.1, 8.8, -79.5, 9.4),
    'Strait of Hormuz': (56.0, 26.0, 57.0, 27.0),
    'Strait of Malacca': (101.0, 1.5, 104.0, 3.5),
    'Bab el Mandeb': (43.0, 12.4, 43.6, 13.0),
    'Strait of Gibraltar': (-6.0, 35.8, -5.2, 36.2),
    'English Channel': (1.0, 50.8, 1.8, 51.2),
    'Bosphorus': (28.9, 41.0, 29.2, 41.3)
}

for name, bbox in straits.items():
    print(f"\n=== Inspecting {name} (bbox: {bbox}) ===")
    try:
        gdf = pyogrio.read_dataframe(shp_path, bbox=bbox, columns=[])
        print(f"Found {len(gdf)} water polygons in bbox")
        if len(gdf) > 0:
            total_area = gdf.geometry.area.sum()
            print(f"Total bbox area: {box(*bbox).area:.4f}, water area: {total_area:.4f}")
            # Check bounding boxes of geometries
            for idx, g in enumerate(gdf.geometry[:5]):
                print(f"  Geom {idx}: type={g.geom_type}, bounds={[round(x, 4) for x in g.bounds]}")
    except Exception as e:
        print(f"Error inspecting {name}: {e}")
