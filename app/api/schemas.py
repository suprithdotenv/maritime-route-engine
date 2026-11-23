from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    lon: float = Field(..., description="Longitude in decimal degrees between -180.0 and 180.0")
    lat: float = Field(..., description="Latitude in decimal degrees between -90.0 and 90.0")

    @field_validator("lon")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude {v} must be between -180.0 and 180.0")
        return v

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude {v} must be between -90.0 and 90.0")
        return v


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    refinement_level: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Regional refinement level (1: coarse regional, 2: medium, 3: high)"
    )


class RouteResponse(BaseModel):
    route_found: bool
    coordinates: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Ordered sequence of (lon, lat) coordinates defining the computed route"
    )
    total_distance_km: float
    global_nodes_count: int
    global_edges_count: int
    regional_nodes_count: int
    regional_edges_count: int
    refinement_level_reached: int
    traversed_chokepoints: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error_detail: Optional[str] = None


class RouteDebugResponse(RouteResponse):
    debug: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    features_count: int
    graph_loaded: bool
    graph_nodes: int
    graph_edges: int
    supported_chokepoints: List[str]
    unsupported_chokepoints: List[str]


class RootResponse(BaseModel):
    app_name: str
    version: str
    status: str
    supported_functionality: List[str]
