import os
import time
import logging
from pathlib import Path
from typing import Tuple, List, Any
import geopandas as gpd
import pyogrio
import numpy as np
from shapely.geometry.base import BaseGeometry

from app.core.config import settings

logger = logging.getLogger(__name__)


class WaterDataLoader:
    def __init__(
        self,
        shapefile_path: Path = settings.shapefile_path,
        parquet_cache_path: Path = settings.parquet_cache_path
    ):
        self.shapefile_path = Path(shapefile_path)
        self.parquet_cache_path = Path(parquet_cache_path)
        self._geometries: np.ndarray = None
        self._crs: str = "EPSG:4326"
        self._is_loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def geometries(self) -> np.ndarray:
        if self._geometries is None:
            self.load()
        return self._geometries

    @property
    def crs(self) -> str:
        return self._crs

    def load(self) -> np.ndarray:
        """Load water polygon geometries, using cached parquet if available, otherwise shapefile."""
        if self._geometries is not None:
            return self._geometries

        t0 = time.time()
        if self.parquet_cache_path.exists():
            logger.info(f"Loading water polygons from cache: {self.parquet_cache_path}")
            gdf = gpd.read_parquet(self.parquet_cache_path)
            self._geometries = gdf.geometry.values
            self._crs = str(gdf.crs) if gdf.crs else "EPSG:4326"
            logger.info(f"Loaded {len(self._geometries)} geometries in {time.time()-t0:.2f}s")
        elif self.shapefile_path.exists():
            logger.info(f"Cache not found. Reading original shapefile: {self.shapefile_path}")
            # Ensure cache dir exists
            self.parquet_cache_path.parent.mkdir(parents=True, exist_ok=True)
            gdf = pyogrio.read_dataframe(self.shapefile_path, columns=[])
            self._geometries = gdf.geometry.values
            self._crs = str(gdf.crs) if gdf.crs else "EPSG:4326"
            logger.info(f"Read shapefile in {time.time()-t0:.2f}s. Saving parquet cache...")
            try:
                gdf.to_parquet(self.parquet_cache_path)
                logger.info(f"Saved cache to {self.parquet_cache_path}")
            except Exception as e:
                logger.warning(f"Could not write cache: {e}")
        else:
            raise FileNotFoundError(
                f"Neither parquet cache ({self.parquet_cache_path}) nor shapefile ({self.shapefile_path}) found!"
            )

        self._is_loaded = True
        return self._geometries


# Singleton instance
data_loader = WaterDataLoader()
