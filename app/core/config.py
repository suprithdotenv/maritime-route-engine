from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SHAPEFILE_DIR = DATA_DIR / "water-polygons-split-4326"
SHAPEFILE_PATH = SHAPEFILE_DIR / "water_polygons.shp"
CACHE_DIR = DATA_DIR / "cache"
PARQUET_CACHE_PATH = CACHE_DIR / "water_polygons.parquet"
GLOBAL_GRAPH_CACHE_PATH = CACHE_DIR / "global_graph.pickle"


class Settings(BaseModel):
    app_name: str = "VoyageIQ — Maritime Routing Engine"
    app_version: str = "1.0.0"
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    shapefile_path: Path = SHAPEFILE_PATH
    cache_dir: Path = CACHE_DIR
    parquet_cache_path: Path = PARQUET_CACHE_PATH
    global_graph_cache_path: Path = GLOBAL_GRAPH_CACHE_PATH

    # Routing settings
    global_grid_step_deg: float = 3.5  # coarse grid for global connectivity
    corridor_buffer_km: float = 200.0  # corridor buffer width around coarse route
    refinement_grid_step_deg: float = 1.0  # finer grid inside corridor
    max_refinement_levels: int = 3
    edge_validation_step_km: float = 15.0  # step size when checking line points against water
    port_snap_radius_deg: float = 0.5  # search radius to snap dock coordinate to water (~55km)


settings = Settings()
