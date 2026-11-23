import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.core.config import settings
from app.geo.data_loader import data_loader
from app.geo.spatial_index import spatial_index
from app.routing.global_graph import global_graph
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("voyageiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler: Preloads data and global routing graph upon server startup."""
    logger.info("Initializing VoyageIQ Maritime Routing Engine...")
    try:
        # 1. Load water polygons data
        data_loader.load()
        # 2. Build STRtree spatial index
        spatial_index.initialize()
        # 3. Load or build global routing graph
        global_graph.load_or_build()
        logger.info("Initialization complete. Engine ready for queries.")
    except Exception as e:
        logger.exception(f"Startup warning during initialization: {e}")
    yield
    logger.info("Shutting down VoyageIQ Maritime Routing Engine...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Hierarchical Maritime Shortest-Path Routing Engine MVP with Narrow Strait Navigation",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes at both root and /api prefix for seamless frontend integration
app.include_router(router)
app.include_router(router, prefix="/api")

# Static frontend assets mount
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/ui", response_class=FileResponse)
    async def get_ui():
        """Serve the VoyageIQ Interactive Maritime Navigation Dashboard."""
        return FileResponse(frontend_dist / "index.html")

    @app.get("/map", response_class=RedirectResponse)
    async def redirect_map():
        """Redirect /map to /ui."""
        return RedirectResponse(url="/ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
