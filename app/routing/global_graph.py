import logging
import pickle
import time
from pathlib import Path
from typing import Tuple, List, Optional
import networkx as nx
import numpy as np
from shapely.geometry import Point
from shapely.strtree import STRtree

from app.core.config import settings
from app.geo.spatial_index import spatial_index
from app.geo.geometry import geodesic_distance_km
from app.routing.chokepoints import get_supported_chokepoints

logger = logging.getLogger(__name__)


class GlobalRoutingGraph:
    def __init__(
        self,
        cache_path: Path = settings.global_graph_cache_path,
        grid_step_deg: float = settings.global_grid_step_deg
    ):
        self.cache_path = Path(cache_path)
        self.grid_step_deg = grid_step_deg
        self._graph: Optional[nx.Graph] = None
        self._node_tree: Optional[STRtree] = None
        self._nodes_list: Optional[List[Tuple[float, float]]] = None

    @property
    def graph(self) -> nx.Graph:
        if self._graph is None:
            self.load_or_build()
        return self._graph

    @property
    def nodes_list(self) -> List[Tuple[float, float]]:
        if self._nodes_list is None:
            self._nodes_list = list(self.graph.nodes)
        return self._nodes_list

    @property
    def node_tree(self) -> STRtree:
        if self._node_tree is None:
            points = [Point(n) for n in self.nodes_list]
            self._node_tree = STRtree(points)
        return self._node_tree

    def load_or_build(self) -> nx.Graph:
        """Load global routing graph from cache if exists, otherwise construct and cache it."""
        if self._graph is not None:
            return self._graph

        if self.cache_path.exists():
            logger.info(f"Loading global routing graph from cache: {self.cache_path}")
            t0 = time.time()
            with open(self.cache_path, "rb") as f:
                self._graph = pickle.load(f)
            logger.info(
                f"Loaded graph with {self._graph.number_of_nodes()} nodes and "
                f"{self._graph.number_of_edges()} edges in {time.time()-t0:.2f}s"
            )
            return self._graph

        logger.info("Building global sparse maritime graph from scratch...")
        t0 = time.time()
        G = nx.Graph()

        # 1. Generate coarse ocean grid
        logger.info(f"Sampling global grid at {self.grid_step_deg} deg spacing...")
        lats = np.arange(-70.0, 75.0, self.grid_step_deg)
        lons = np.arange(-180.0, 180.0, self.grid_step_deg)

        ocean_nodes = []
        for lat in lats:
            for lon in lons:
                coord = (round(float(lon), 4), round(float(lat), 4))
                if spatial_index.is_point_in_water(coord[0], coord[1]):
                    ocean_nodes.append(coord)
                    G.add_node(coord, node_type="ocean_grid")

        logger.info(f"Found {len(ocean_nodes)} navigable ocean grid nodes.")

        # 2. Add verified chokepoint corridor nodes and edges
        chokepoints = get_supported_chokepoints()
        chokepoint_endpoints = []
        for chk_key, chk_data in chokepoints.items():
            corridor = chk_data["corridor"]
            logger.info(f"Adding chokepoint '{chk_data['name']}' with {len(corridor)} waypoints...")
            for i, pt in enumerate(corridor):
                coord = (round(float(pt[0]), 4), round(float(pt[1]), 4))
                G.add_node(coord, node_type="chokepoint", chokepoint=chk_key)
                if i > 0:
                    prev = (round(float(corridor[i - 1][0]), 4), round(float(corridor[i - 1][1]), 4))
                    dist = geodesic_distance_km(prev, coord)
                    G.add_edge(prev, coord, weight=dist, edge_type="chokepoint_corridor")

            chokepoint_endpoints.append((round(float(corridor[0][0]), 4), round(float(corridor[0][1]), 4)))
            chokepoint_endpoints.append((round(float(corridor[-1][0]), 4), round(float(corridor[-1][1]), 4)))

        # 3. Build spatial index over all nodes to quickly find candidate edges
        all_nodes = list(G.nodes)
        node_pts = [Point(n) for n in all_nodes]
        tree = STRtree(node_pts)

        # Max edge connection distance: ~1.8x grid step in degrees
        max_search_deg = self.grid_step_deg * 1.8
        logger.info(f"Connecting grid edges (search radius {max_search_deg:.1f} deg)...")

        edge_count = 0
        for i, n1 in enumerate(all_nodes):
            if G.nodes[n1].get("node_type") != "ocean_grid":
                continue
            pt1 = Point(n1)
            cands = tree.query(pt1.buffer(max_search_deg))
            for c in cands:
                if c > i:
                    n2 = all_nodes[c]
                    if G.nodes[n2].get("node_type") != "ocean_grid":
                        continue
                    d_km = geodesic_distance_km(n1, n2)
                    if d_km < 700.0:
                        if spatial_index.is_edge_valid(n1, n2, max_step_km=15.0):
                            G.add_edge(n1, n2, weight=d_km, edge_type="ocean_edge")
                            edge_count += 1

        # Connect chokepoint endpoints to nearest visible ocean nodes
        for ep in chokepoint_endpoints:
            pt_ep = Point(ep)
            cands = tree.query(pt_ep.buffer(max_search_deg * 2.0))
            for c in cands:
                n2 = all_nodes[c]
                if n2 != ep and G.nodes[n2].get("node_type") == "ocean_grid":
                    d_km = geodesic_distance_km(ep, n2)
                    if d_km < 900.0 and spatial_index.is_edge_valid(ep, n2, max_step_km=10.0):
                        G.add_edge(ep, n2, weight=d_km, edge_type="portal_connection")

        logger.info(
            f"Global graph constructed in {time.time()-t0:.2f}s with "
            f"{G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
        )

        # Save to cache
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "wb") as f:
            pickle.dump(G, f)
        logger.info(f"Saved global graph cache to {self.cache_path}")

        self._graph = G
        return self._graph


# Singleton instance
global_graph = GlobalRoutingGraph()
