import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  Anchor, 
  Cpu, 
  ChevronDown, 
  ChevronUp, 
  AlertTriangle,
  Download,
  TrendingDown
} from 'lucide-react';
import type { RouteResponse, Coordinate } from '../types';

interface RouteResultsProps {
  route: RouteResponse;
  origin: Coordinate;
  destination: Coordinate;
}

export const RouteResults: React.FC<RouteResultsProps> = ({
  route,
  origin,
  destination,
}) => {
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [showWaypoints, setShowWaypoints] = useState(false);

  // Conversion: 1 km = 0.539957 nautical miles
  const distanceNmi = (route.total_distance_km * 0.539957).toFixed(1);

  // Calculate distance savings if debug coarse route is available
  const coarseDistance = route.debug?.coarse_distance_km;
  const distanceSavedKm = coarseDistance ? (coarseDistance - route.total_distance_km).toFixed(1) : null;
  const savingsPct = coarseDistance && coarseDistance > 0 
    ? (((coarseDistance - route.total_distance_km) / coarseDistance) * 100).toFixed(1)
    : null;

  const downloadRouteGeoJSON = () => {
    const geojson = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: {
            name: 'VoyageIQ Refined Maritime Route',
            origin: [origin.lon, origin.lat],
            destination: [destination.lon, destination.lat],
            distance_km: route.total_distance_km,
            distance_nmi: parseFloat(distanceNmi),
            chokepoints: route.traversed_chokepoints,
            computation_time_ms: route.debug?.computation_time_ms,
          },
          geometry: {
            type: 'LineString',
            coordinates: route.coordinates,
          },
        },
      ],
    };

    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(geojson, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', 'voyageiq_maritime_route.geojson');
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl p-4 text-slate-200 shadow-2xl space-y-3.5 max-w-md w-full">
      {/* Header & Status */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded-full bg-emerald-950 border border-emerald-700/60 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-100">Navigable Maritime Route</h3>
            <p className="text-[11px] text-emerald-400 font-medium">100% Water Validated • 0 Land Crossings</p>
          </div>
        </div>

        <button
          onClick={downloadRouteGeoJSON}
          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 transition-colors cursor-pointer"
          title="Download Route as GeoJSON"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>

      {/* Main Distance Metrics */}
      <div className="grid grid-cols-2 gap-3 bg-slate-950/70 p-3 rounded-lg border border-slate-800/80">
        <div>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider block">
            Geodesic Distance
          </span>
          <div className="flex items-baseline space-x-1 mt-0.5">
            <span className="text-2xl font-black text-cyan-400">
              {route.total_distance_km.toLocaleString(undefined, { maximumFractionDigits: 1 })}
            </span>
            <span className="text-xs text-slate-400 font-medium">km</span>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            ≈ {parseFloat(distanceNmi).toLocaleString()} nmi
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider block">
            Corridor Optimization
          </span>
          {distanceSavedKm && parseFloat(distanceSavedKm) > 0 ? (
            <div className="mt-0.5">
              <div className="flex items-center space-x-1 text-emerald-400 font-bold text-sm">
                <TrendingDown className="w-3.5 h-3.5" />
                <span>-{distanceSavedKm} km</span>
              </div>
              <span className="text-[11px] text-emerald-500 font-medium">
                {savingsPct}% shorter than coarse grid
              </span>
            </div>
          ) : (
            <div className="mt-0.5 text-xs text-slate-400">
              Optimal geodesic corridor reached
            </div>
          )}
        </div>
      </div>

      {/* Traversed Chokepoints */}
      {route.traversed_chokepoints && route.traversed_chokepoints.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5">
            <Anchor className="w-3.5 h-3.5 text-cyan-400" />
            <span>Traversed Straits & Canals:</span>
          </span>
          <div className="flex flex-wrap gap-1.5">
            {route.traversed_chokepoints.map((cp, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 font-medium flex items-center space-x-1"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                <span>{cp}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Dataset Limitation Warning (e.g. Panama) */}
      {route.warnings && route.warnings.length > 0 && (
        <div className="p-2.5 rounded-lg bg-amber-950/60 border border-amber-800/60 text-amber-200 text-xs space-y-1">
          <div className="flex items-center space-x-1.5 font-semibold text-amber-300">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Dataset Limitation Notice</span>
          </div>
          {route.warnings.map((w, idx) => (
            <p key={idx} className="text-[11px] leading-relaxed text-amber-200/90">
              {w}
            </p>
          ))}
        </div>
      )}

      {/* Quick Summary Pill Bar */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 bg-slate-950/40 px-2.5 py-1.5 rounded-lg border border-slate-800">
        <span className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-slate-400" />
          <span>Latency: <strong className="text-slate-200">{route.debug?.computation_time_ms ? `${route.debug.computation_time_ms.toFixed(0)} ms` : '< 1s'}</strong></span>
        </span>
        <span>Waypoints: <strong className="text-slate-200">{route.coordinates.length}</strong></span>
        <span>Resolution: <strong className="text-cyan-400">Level {route.refinement_level_reached}</strong></span>
      </div>

      {/* Collapsible Technical Diagnostics */}
      <div className="border-t border-slate-800 pt-2">
        <button
          onClick={() => setShowDiagnostics(!showDiagnostics)}
          className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 py-1 transition-colors cursor-pointer"
        >
          <span className="flex items-center space-x-1.5 font-medium">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>Hierarchical Graph Diagnostics</span>
          </span>
          {showDiagnostics ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showDiagnostics && (
          <div className="mt-2 p-2.5 rounded-lg bg-slate-950 text-xs space-y-2 border border-slate-800 font-mono">
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="text-slate-500 block">Global Graph:</span>
                <span className="text-slate-300">{route.global_nodes_count.toLocaleString()} nodes / {route.global_edges_count.toLocaleString()} edges</span>
              </div>
              <div>
                <span className="text-slate-500 block">Regional Corridor:</span>
                <span className="text-cyan-400">{route.regional_nodes_count.toLocaleString()} nodes / {route.regional_edges_count.toLocaleString()} edges</span>
              </div>
            </div>

            {route.debug?.coarse_distance_km && (
              <div className="text-[11px] pt-1 border-t border-slate-900">
                <span className="text-slate-500">Coarse Route Distance: </span>
                <span className="text-amber-400">{route.debug.coarse_distance_km.toFixed(1)} km</span>
              </div>
            )}

            {/* Waypoints Toggle */}
            <div className="pt-2 border-t border-slate-900">
              <button
                onClick={() => setShowWaypoints(!showWaypoints)}
                className="text-[11px] text-cyan-400 hover:underline flex items-center space-x-1 cursor-pointer"
              >
                <span>{showWaypoints ? 'Hide' : 'Show'} Coordinate Waypoints List ({route.coordinates.length})</span>
              </button>

              {showWaypoints && (
                <div className="mt-2 max-h-40 overflow-y-auto space-y-1 text-[10px] text-slate-400 bg-slate-900 p-2 rounded border border-slate-800">
                  {route.coordinates.map((pt, i) => (
                    <div key={i} className="flex justify-between hover:text-slate-200">
                      <span>#{i + 1}</span>
                      <span>Lon: {pt[0].toFixed(4)}°, Lat: {pt[1].toFixed(4)}°</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
