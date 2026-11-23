import logging
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.api.schemas import (
    RootResponse,
    HealthResponse,
    RouteRequest,
    RouteResponse,
    RouteDebugResponse
)
from app.geo.data_loader import data_loader
from app.geo.spatial_index import spatial_index
from app.routing.global_graph import global_graph
from app.routing.chokepoints import get_supported_chokepoints, get_unsupported_chokepoints
from app.services.routing_service import routing_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=RootResponse)
def get_root():
    """Return API metadata, status, and supported functionality."""
    return RootResponse(
        app_name=settings.app_name,
        version=settings.app_version,
        status="online",
        supported_functionality=[
            "Global maritime shortest-path routing (Dijkstra / A*)",
            "Geodesic distance calculation on WGS84 ellipsoid",
            "Geometric validation against 1.2 GB OpenStreetMap water polygons",
            "Regional corridor route refinement without global graph blowup",
            "Narrow-strait and canal navigation (Suez Canal, Malacca, Hormuz, Dover, Gibraltar, Bab-el-Mandeb)",
            "Chokepoint dataset limitation reporting (Panama Canal freshwater locks)",
            "Line-of-sight nautical route smoothing and shortcutting",
            "Comprehensive route debugging and diagnostics"
        ]
    )


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Return application health, data load status, and graph dimensions."""
    geoms = data_loader.geometries
    data_loaded = (geoms is not None and len(geoms) > 0)
    features_count = len(geoms) if data_loaded else 0

    g = global_graph.graph
    graph_loaded = (g is not None)
    graph_nodes = g.number_of_nodes() if graph_loaded else 0
    graph_edges = g.number_of_edges() if graph_loaded else 0

    supported = list(get_supported_chokepoints().keys())
    unsupported = list(get_unsupported_chokepoints().keys())

    return HealthResponse(
        status="healthy",
        data_loaded=data_loaded,
        features_count=features_count,
        graph_loaded=graph_loaded,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        supported_chokepoints=supported,
        unsupported_chokepoints=unsupported
    )


@router.post("/route", response_model=RouteResponse)
def calculate_route(request: RouteRequest):
    """Compute the shortest maritime route between origin and destination."""
    try:
        origin_pt = (request.origin.lon, request.origin.lat)
        dest_pt = (request.destination.lon, request.destination.lat)

        result = routing_service.calculate_route(
            origin=origin_pt,
            destination=dest_pt,
            refinement_level=request.refinement_level,
            include_debug=False
        )
        return RouteResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error computing route")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing internal error: {str(e)}"
        )


@router.post("/route/debug", response_model=RouteDebugResponse)
def calculate_route_debug(request: RouteRequest):
    """Compute maritime route and return comprehensive diagnostic development data."""
    try:
        origin_pt = (request.origin.lon, request.origin.lat)
        dest_pt = (request.destination.lon, request.destination.lat)

        result = routing_service.calculate_route(
            origin=origin_pt,
            destination=dest_pt,
            refinement_level=request.refinement_level,
            include_debug=True
        )
        return RouteDebugResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error computing route with debug")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing debug internal error: {str(e)}"
        )
