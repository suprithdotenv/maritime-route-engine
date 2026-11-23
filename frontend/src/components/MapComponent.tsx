import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Maximize2, Crosshair } from 'lucide-react';
import type { Coordinate, RouteResponse } from '../types';
import { CHOKEPOINTS } from '../data/chokepoints';

interface MapComponentProps {
  origin: Coordinate;
  destination: Coordinate;
  route: RouteResponse | null;
  pickMode: 'origin' | 'destination' | null;
  onMapClick: (coord: Coordinate) => void;
  showCoarseRoute: boolean;
  showRefinedRoute: boolean;
  showChokepoints: boolean;
  targetView: { lon: number; lat: number; zoom: number } | null;
}

// Convert GeoJSON [lon, lat] to Leaflet [lat, lon]
const toLatLng = (pt: [number, number]): [number, number] => [pt[1], pt[0]];

// Break lines crossing the antimeridian to prevent wrap-around lines
function splitAntimeridian(pts: [number, number][]): [number, number][][] {
  if (pts.length === 0) return [];
  const segments: [number, number][][] = [];
  let currentSegment: [number, number][] = [pts[0]];

  for (let i = 1; i < pts.length; i++) {
    const prevLon = pts[i - 1][0];
    const currLon = pts[i][0];
    // If longitude jump exceeds 180 degrees, it crosses the date line
    if (Math.abs(currLon - prevLon) > 180) {
      segments.push(currentSegment);
      currentSegment = [pts[i]];
    } else {
      currentSegment.push(pts[i]);
    }
  }
  if (currentSegment.length > 0) {
    segments.push(currentSegment);
  }
  return segments;
}

export const MapComponent: React.FC<MapComponentProps> = ({
  origin,
  destination,
  route,
  pickMode,
  onMapClick,
  showCoarseRoute,
  showRefinedRoute,
  showChokepoints,
  targetView,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Layer groups
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const chokepointsLayerRef = useRef<L.LayerGroup | null>(null);
  const coarseRouteLayerRef = useRef<L.LayerGroup | null>(null);
  const refinedRouteLayerRef = useRef<L.LayerGroup | null>(null);

  // 1. Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20.0, 55.0], // Centered around Arabian Sea / Indian Ocean
      zoom: 3,
      minZoom: 2,
      maxZoom: 18,
      zoomControl: false,
      worldCopyJump: true,
    });

    // Zoom control in bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // 1. Esri Ocean Basemap (Default, genuine nautical ocean bathymetry, 100% free, no API key)
    const oceanBase = L.tileLayer('https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; GEBCO, NOAA, National Geographic',
      maxZoom: 13,
    });
    const oceanRef = L.tileLayer('https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 13,
    });
    const oceanGroup = L.layerGroup([oceanBase, oceanRef]);

    // 2. OpenStreetMap Standard (100% free, no API key)
    const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    });

    // 3. Esri Dark Gray Nautical Canvas (100% free, no API key)
    const darkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri',
      maxZoom: 16,
    });
    const darkRef = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16,
    });
    const darkGroup = L.layerGroup([darkBase, darkRef]);

    // 4. Esri Satellite / World Imagery (100% free, no API key)
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Earthstar Geographics',
      maxZoom: 18,
    });

    // Default to Ocean Basemap
    oceanGroup.addTo(map);

    // Add layer selector to top right
    const baseMaps = {
      '🌊 Ocean Basemap': oceanGroup,
      '🗺️ OpenStreetMap': osm,
      '🌑 Dark Canvas': darkGroup,
      '🛰️ Satellite Imagery': satellite,
    };
    L.control.layers(baseMaps, undefined, { position: 'topright' }).addTo(map);

    // Initialize layer groups
    markersLayerRef.current = L.layerGroup().addTo(map);
    chokepointsLayerRef.current = L.layerGroup().addTo(map);
    coarseRouteLayerRef.current = L.layerGroup().addTo(map);
    refinedRouteLayerRef.current = L.layerGroup().addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // 2. Handle map clicks for Pick on Map
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const handleClick = (e: L.LeafletMouseEvent) => {
      if (pickMode) {
        onMapClick({
          lon: parseFloat(e.latlng.lng.toFixed(4)),
          lat: parseFloat(e.latlng.lat.toFixed(4)),
        });
      }
    };

    map.on('click', handleClick);
    return () => {
      map.off('click', handleClick);
    };
  }, [pickMode, onMapClick]);

  // 3. Update cursor style when in pickMode
  useEffect(() => {
    if (mapContainerRef.current) {
      if (pickMode) {
        mapContainerRef.current.style.cursor = 'crosshair';
      } else {
        mapContainerRef.current.style.cursor = '';
      }
    }
  }, [pickMode]);

  // 4. Update Target View when chokepoints or jump buttons clicked
  useEffect(() => {
    if (!mapInstanceRef.current || !targetView) return;
    mapInstanceRef.current.flyTo([targetView.lat, targetView.lon], targetView.zoom, {
      duration: 1.5,
    });
  }, [targetView]);

  // 5. Render Origin & Destination Markers
  useEffect(() => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();

    // Custom Origin Icon (Emerald Green Beacon)
    const originIcon = L.divIcon({
      className: 'custom-origin-icon',
      html: `
        <div style="position: relative; width: 24px; height: 24px;">
          <div class="marker-pulse-emerald"></div>
          <div style="
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: #10b981;
            border: 2px solid #ffffff;
            border-radius: 50%;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #022c22;
            font-weight: bold;
            font-size: 11px;
          ">O</div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    // Custom Destination Icon (Crimson Red Beacon)
    const destIcon = L.divIcon({
      className: 'custom-dest-icon',
      html: `
        <div style="position: relative; width: 24px; height: 24px;">
          <div class="marker-pulse-rose"></div>
          <div style="
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: #f43f5e;
            border: 2px solid #ffffff;
            border-radius: 50%;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #4c0519;
            font-weight: bold;
            font-size: 11px;
          ">D</div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const originMarker = L.marker([origin.lat, origin.lon], { icon: originIcon })
      .bindPopup(`
        <div style="font-size: 12px; font-family: sans-serif;">
          <strong style="color: #10b981;">Departure / Origin</strong><br/>
          <span>Lon: ${origin.lon.toFixed(4)}°</span><br/>
          <span>Lat: ${origin.lat.toFixed(4)}°</span>
        </div>
      `);
    markersLayerRef.current.addLayer(originMarker);

    const destMarker = L.marker([destination.lat, destination.lon], { icon: destIcon })
      .bindPopup(`
        <div style="font-size: 12px; font-family: sans-serif;">
          <strong style="color: #f43f5e;">Destination Port</strong><br/>
          <span>Lon: ${destination.lon.toFixed(4)}°</span><br/>
          <span>Lat: ${destination.lat.toFixed(4)}°</span>
        </div>
      `);
    markersLayerRef.current.addLayer(destMarker);
  }, [origin, destination]);

  // 6. Render Chokepoints Layer
  useEffect(() => {
    if (!chokepointsLayerRef.current) return;
    chokepointsLayerRef.current.clearLayers();

    if (!showChokepoints) return;

    CHOKEPOINTS.forEach((cp) => {
      const chokepointIcon = L.divIcon({
        className: 'chokepoint-icon',
        html: `
          <div style="
            width: 20px;
            height: 20px;
            background: ${cp.supported ? '#f59e0b' : '#ef4444'};
            border: 2px solid #0f172a;
            border-radius: 4px;
            transform: rotate(45deg);
            box-shadow: 0 2px 6px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="transform: rotate(-45deg); font-size: 9px; font-weight: 800; color: #0f172a;">
              ${cp.supported ? '⚓' : '✕'}
            </div>
          </div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });

      const marker = L.marker([cp.lat, cp.lon], { icon: chokepointIcon })
        .bindPopup(`
          <div style="font-size: 12px; max-width: 220px;">
            <div style="font-weight: bold; color: ${cp.supported ? '#f59e0b' : '#ef4444'};">
              ${cp.name}
            </div>
            <div style="font-size: 10px; color: #94a3b8; margin: 4px 0;">
              ${cp.description}
            </div>
            <span style="
              display: inline-block;
              font-size: 10px;
              padding: 2px 6px;
              border-radius: 4px;
              background: ${cp.supported ? '#064e3b' : '#450a0a'};
              color: ${cp.supported ? '#6ee7b7' : '#fca5a5'};
            ">
              ${cp.supported ? 'Navigable Pass' : 'Dataset Gap'}
            </span>
          </div>
        `);
      chokepointsLayerRef.current?.addLayer(marker);
    });
  }, [showChokepoints]);

  // 7. Render Coarse Global Route (Dashed amber)
  useEffect(() => {
    if (!coarseRouteLayerRef.current) return;
    coarseRouteLayerRef.current.clearLayers();

    if (!showCoarseRoute || !route?.debug?.coarse_route) return;

    const segments = splitAntimeridian(route.debug.coarse_route);
    segments.forEach((seg) => {
      const latLngs = seg.map(toLatLng);
      const poly = L.polyline(latLngs, {
        color: '#f59e0b',
        weight: 3,
        dashArray: '6, 8',
        opacity: 0.85,
      }).bindTooltip(`Coarse Global Route (${route.debug?.coarse_distance_km.toFixed(1)} km)`);
      coarseRouteLayerRef.current?.addLayer(poly);
    });
  }, [route, showCoarseRoute]);

  // 8. Render Refined Maritime Route (Glowing cyan)
  useEffect(() => {
    if (!refinedRouteLayerRef.current) return;
    refinedRouteLayerRef.current.clearLayers();

    if (!showRefinedRoute || !route?.coordinates || route.coordinates.length < 2) return;

    const segments = splitAntimeridian(route.coordinates);
    segments.forEach((seg) => {
      const latLngs = seg.map(toLatLng);

      // Glow casing line
      const casing = L.polyline(latLngs, {
        color: '#0891b2',
        weight: 8,
        opacity: 0.35,
      });
      refinedRouteLayerRef.current?.addLayer(casing);

      // Core crisp polyline
      const poly = L.polyline(latLngs, {
        color: '#06b6d4',
        weight: 4.5,
        opacity: 0.95,
      }).bindTooltip(`Refined Maritime Route (${route.total_distance_km.toFixed(1)} km)`);
      refinedRouteLayerRef.current?.addLayer(poly);
    });

    // Auto-fit bounds on new route
    if (mapInstanceRef.current && route.coordinates.length > 0) {
      const allLatLngs = route.coordinates.map(toLatLng);
      const bounds = L.latLngBounds(allLatLngs);
      mapInstanceRef.current.fitBounds(bounds, { padding: [60, 60], maxZoom: 8 });
    }
  }, [route, showRefinedRoute]);

  // Handler to Fit Route manually
  const handleFitRoute = () => {
    if (!mapInstanceRef.current) return;
    if (route && route.coordinates.length > 0) {
      const allLatLngs = route.coordinates.map(toLatLng);
      mapInstanceRef.current.fitBounds(L.latLngBounds(allLatLngs), { padding: [60, 60] });
    } else {
      mapInstanceRef.current.fitBounds(
        L.latLngBounds([[origin.lat, origin.lon], [destination.lat, destination.lon]]),
        { padding: [80, 80] }
      );
    }
  };

  return (
    <div className="relative w-full h-full">
      {/* Leaflet DOM Node */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Crosshair click banner when Pick Mode is active */}
      {pickMode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 bg-slate-900/95 backdrop-blur border border-cyan-500/80 text-cyan-300 px-4 py-2 rounded-full shadow-2xl flex items-center space-x-2 text-xs font-semibold animate-pulse">
          <Crosshair className="w-4 h-4 text-cyan-400" />
          <span>Click anywhere on navigable water to place {pickMode === 'origin' ? 'Departure' : 'Destination'}</span>
        </div>
      )}

      {/* Floating Action Buttons (Fit Route) */}
      <div className="absolute bottom-6 right-6 z-20 flex flex-col space-y-2">
        <button
          type="button"
          onClick={handleFitRoute}
          className="p-3 rounded-xl bg-slate-900/90 backdrop-blur border border-slate-700 text-slate-200 hover:text-cyan-400 hover:border-cyan-500 shadow-xl transition-all active:scale-95 flex items-center justify-center cursor-pointer"
          title="Fit Route to Screen"
        >
          <Maximize2 className="w-5 h-5" />
        </button>
      </div>

      {/* Floating Map Legend */}
      <div className="absolute bottom-6 left-6 z-20 bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-xl p-3 text-xs text-slate-300 shadow-xl hidden md:block space-y-2">
        <div className="font-semibold text-slate-200 text-[11px] uppercase tracking-wider">Map Legend</div>
        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/30" />
            <span>Departure / Origin</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/30" />
            <span>Destination Port</span>
          </div>
          {showRefinedRoute && (
            <div className="flex items-center space-x-2">
              <span className="w-4 h-1 bg-cyan-400 rounded" />
              <span>Refined Maritime Route</span>
            </div>
          )}
          {showCoarseRoute && (
            <div className="flex items-center space-x-2">
              <span className="w-4 h-0.5 border-t-2 border-dashed border-amber-400" />
              <span>Coarse Global Route</span>
            </div>
          )}
          {showChokepoints && (
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rotate-45 bg-amber-500 inline-block" />
              <span>Maritime Chokepoint</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
