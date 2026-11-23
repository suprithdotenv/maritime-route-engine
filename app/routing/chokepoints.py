from typing import List, Tuple, Dict, Any

CHOKEPOINTS: Dict[str, Dict[str, Any]] = {
    "suez_canal": {
        "name": "Suez Canal & Red Sea Corridor",
        "description": "Navigable corridor connecting Mediterranean Sea through Suez Canal and Red Sea to Bab-el-Mandeb",
        "bbox": (32.0, 13.5, 43.0, 32.0),
        "supported": True,
        # Exact verified navigable sequence from Mediterranean Sea through Suez Canal and Red Sea
        "corridor": [
            (32.304, 31.300),     # Mediterranean Approach North
            (32.307, 31.174),     # Port Said Channel
            (32.310, 31.024),     # El Qantara North
            (32.316, 30.879),     # El Qantara South
            (32.319, 30.807),     # El Ballah
            (32.352, 30.681),     # El Firdan
            (32.331, 30.591),     # Lake Timsah / Ismailia
            (32.358, 30.444),     # Deversoir Approach
            (32.370, 30.405),     # Great Bitter Lake North
            (32.466, 30.276),     # Great Bitter Lake Central
            (32.535, 30.234),     # Little Bitter Lake
            (32.568, 30.171),     # Kabret Channel
            (32.574, 30.045),     # Geneifa / El Shallufa
            (32.583, 30.000),     # Port Tewfik Approach North
            (32.545, 29.735),     # Gulf of Suez North
            (32.530, 29.500),     # Gulf of Suez Open Water
            (33.800, 27.800),     # Straits of Gubal
            (35.000, 26.500),     # Northern Red Sea
            (36.500, 24.500),     # Central-North Red Sea
            (38.000, 22.000),     # Central Red Sea
            (39.500, 19.500),     # Central-South Red Sea
            (41.000, 16.500),     # Southern Red Sea
            (42.500, 13.800),     # Bab-el-Mandeb North Approach (joins bab_el_mandeb corridor)
        ]
    },
    "bab_el_mandeb": {
        "name": "Bab-el-Mandeb Strait",
        "description": "Strait connecting the Red Sea to the Gulf of Aden",
        "bbox": (42.5, 12.0, 44.5, 14.0),
        "supported": True,
        "corridor": [
            (42.50, 13.80),       # Southern Red Sea
            (43.00, 13.00),       # Bab-el-Mandeb North Approach
            (43.35, 12.60),       # Bab-el-Mandeb Chokepoint
            (43.80, 12.30),       # Gulf of Aden West Approach
            (44.50, 12.10),       # Gulf of Aden
        ]
    },
    "strait_of_hormuz": {
        "name": "Strait of Hormuz",
        "description": "Strait between the Persian Gulf and the Gulf of Oman",
        "bbox": (55.0, 25.0, 58.0, 27.5),
        "supported": True,
        "corridor": [
            (55.00, 26.60),       # Central Persian Gulf
            (55.80, 26.40),       # Western Approach
            (56.45, 26.35),       # Strait Chokepoint (Musandam)
            (56.80, 26.00),       # Eastern Chokepoint Exit
            (57.50, 25.40),       # Gulf of Oman
        ]
    },
    "strait_of_malacca": {
        "name": "Strait of Malacca & Singapore Strait",
        "description": "Major waterway connecting the Indian Ocean to the South China Sea",
        "bbox": (97.0, 1.0, 105.0, 6.0),
        "supported": True,
        "corridor": [
            (97.50, 5.50),        # Andaman Sea Entrance
            (99.00, 4.30),        # Northern Malacca
            (100.50, 3.20),       # Central Malacca North
            (101.40, 2.50),       # Central Malacca South
            (102.30, 1.90),       # Southern Malacca
            (103.50, 1.25),       # Western Singapore Strait
            (103.75, 1.15),       # Central Singapore Strait Main Deep Water Channel
            (104.30, 1.30),       # Eastern Singapore Strait
            (105.00, 1.60),       # South China Sea Entrance
        ]
    },
    "strait_of_gibraltar": {
        "name": "Strait of Gibraltar & Alboran Sea Corridor",
        "description": "Strait connecting the Atlantic Ocean to the Mediterranean Sea",
        "bbox": (-7.0, 35.5, 13.0, 38.5),
        "supported": True,
        "corridor": [
            (-6.80, 36.00),       # Atlantic Western Approach
            (-6.00, 35.95),       # Cape Spartel / Trafalgar
            (-5.60, 35.95),       # Tarifa Chokepoint
            (-5.20, 36.05),       # Rock of Gibraltar / Alboran Entrance
            (-4.50, 36.20),       # Alboran Sea / Western Mediterranean
            (-2.00, 36.20),       # Central Alboran Sea
            (1.50, 36.80),        # Western Mediterranean Basin
            (5.00, 37.50),        # Algerian / Balearic Basin
            (8.50, 38.00),        # South of Sardinia
            (12.50, 37.50),       # Strait of Sicily (connects to Mediterranean grid)
        ]
    },
    "english_channel": {
        "name": "English Channel & Strait of Dover",
        "description": "Channel separating Southern England from Northern France",
        "bbox": (-5.0, 49.0, 2.5, 52.0),
        "supported": True,
        "corridor": [
            (-4.50, 49.50),       # Western Approaches
            (-2.50, 50.00),       # Central Channel
            (-0.50, 50.30),       # Eastern Channel
            (1.20, 51.00),        # Strait of Dover Chokepoint
            (1.80, 51.30),        # Dover Exit
            (2.50, 51.80),        # Southern North Sea
        ]
    },
    "panama_canal": {
        "name": "Panama Canal",
        "description": "Canal connecting Pacific Ocean and Caribbean Sea",
        "bbox": (-80.1, 8.8, -79.5, 9.4),
        "supported": False,
        "limitation": (
            "The geographic dataset contains ocean polygons and does not resolve freshwater "
            "inland lock systems (Gatun Lake / Culebra Cut). A continuous navigable water polygon "
            "between Caribbean Sea and Pacific Ocean is not present in the dataset."
        ),
        "corridor": []
    }
}


def get_supported_chokepoints() -> Dict[str, Dict[str, Any]]:
    """Return chokepoints that have continuous water corridor representation in the dataset."""
    return {k: v for k, v in CHOKEPOINTS.items() if v["supported"]}


def get_unsupported_chokepoints() -> Dict[str, Dict[str, Any]]:
    """Return chokepoints with known dataset coverage limitations."""
    return {k: v for k, v in CHOKEPOINTS.items() if not v["supported"]}


def check_for_chokepoint_limitation(origin: Tuple[float, float], destination: Tuple[float, float]) -> List[str]:
    """Check if the route between origin and destination implies traversing an unsupported canal/strait.

    For example, routing between Atlantic/Caribbean and Pacific through Central America.
    """
    warnings = []
    lon1, lat1 = origin
    lon2, lat2 = destination

    is_p1_atlantic = (-100.0 <= lon1 <= -40.0) and (5.0 <= lat1 <= 45.0)
    is_p2_pacific = (-130.0 <= lon2 <= -75.0) and (-20.0 <= lat2 <= 35.0)

    is_p2_atlantic = (-100.0 <= lon2 <= -40.0) and (5.0 <= lat2 <= 45.0)
    is_p1_pacific = (-130.0 <= lon1 <= -75.0) and (-20.0 <= lat1 <= 35.0)

    if (is_p1_atlantic and is_p2_pacific) or (is_p2_atlantic and is_p1_pacific):
        warnings.append(
            "Notice: Direct transit through Panama Canal is not supported by the ocean polygon dataset "
            "because freshwater inland locks/lakes are not resolved. Routes between Atlantic and Pacific "
            "must navigate around South America (Strait of Magellan / Cape Horn) or alternative oceanic corridors."
        )

    return warnings
