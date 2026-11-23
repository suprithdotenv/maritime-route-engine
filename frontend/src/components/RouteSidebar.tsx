import React, { useState } from 'react';
import { 
  Navigation, 
  ArrowUpDown, 
  Crosshair, 
  Sliders, 
  Play, 
  RotateCcw, 
  AlertTriangle,
  ChevronDown,
  Search,
  Sparkles
} from 'lucide-react';
import type { Coordinate } from '../types';
import type { PresetRoute } from '../data/ports';
import { MAJOR_PORTS, PRESET_ROUTES } from '../data/ports';

interface RouteSidebarProps {
  origin: Coordinate;
  destination: Coordinate;
  onOriginChange: (coord: Coordinate) => void;
  onDestinationChange: (coord: Coordinate) => void;
  onSwapCoordinates: () => void;
  pickMode: 'origin' | 'destination' | null;
  onSetPickMode: (mode: 'origin' | 'destination' | null) => void;
  refinementLevel: number;
  onRefinementLevelChange: (level: number) => void;
  showCoarseRoute: boolean;
  onToggleCoarseRoute: (show: boolean) => void;
  showRefinedRoute: boolean;
  onToggleRefinedRoute: (show: boolean) => void;
  showChokepoints: boolean;
  onToggleChokepoints: (show: boolean) => void;
  onCalculateRoute: () => void;
  onClearRoute: () => void;
  isLoading: boolean;
  hasRoute: boolean;
  errorMessage: string | null;
}

export const RouteSidebar: React.FC<RouteSidebarProps> = ({
  origin,
  destination,
  onOriginChange,
  onDestinationChange,
  onSwapCoordinates,
  pickMode,
  onSetPickMode,
  refinementLevel,
  onRefinementLevelChange,
  showCoarseRoute,
  onToggleCoarseRoute,
  showRefinedRoute,
  onToggleRefinedRoute,
  showChokepoints,
  onToggleChokepoints,
  onCalculateRoute,
  onClearRoute,
  isLoading,
  hasRoute,
  errorMessage,
}) => {
  const [showPortSearchOrigin, setShowPortSearchOrigin] = useState(false);
  const [showPortSearchDest, setShowPortSearchDest] = useState(false);
  const [originSearchQuery, setOriginSearchQuery] = useState('');
  const [destSearchQuery, setDestSearchQuery] = useState('');

  const filteredOriginPorts = MAJOR_PORTS.filter(p => 
    p.name.toLowerCase().includes(originSearchQuery.toLowerCase()) ||
    p.country.toLowerCase().includes(originSearchQuery.toLowerCase())
  );

  const filteredDestPorts = MAJOR_PORTS.filter(p => 
    p.name.toLowerCase().includes(destSearchQuery.toLowerCase()) ||
    p.country.toLowerCase().includes(destSearchQuery.toLowerCase())
  );

  const handleSelectPreset = (preset: PresetRoute) => {
    onOriginChange({ lon: preset.origin.lon, lat: preset.origin.lat });
    onDestinationChange({ lon: preset.destination.lon, lat: preset.destination.lat });
    onRefinementLevelChange(preset.level);
    onSetPickMode(null);
  };

  return (
    <div className="w-full md:w-96 bg-slate-900/95 backdrop-blur-md border-r border-slate-800 flex flex-col h-full overflow-y-auto text-slate-200 z-20 shadow-2xl">
      {/* Header Tabs / Title */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-sm">
            <Navigation className="w-4 h-4" />
            <span>Maritime Waypoint Routing</span>
          </div>
          {hasRoute && (
            <button
              onClick={onClearRoute}
              className="text-xs text-slate-400 hover:text-rose-400 flex items-center space-x-1 transition-colors cursor-pointer"
              title="Clear current route"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {/* Origin & Destination Card */}
        <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 relative space-y-3">
          {/* Origin Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center space-x-1.5 text-emerald-400 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/30" />
                <span>Departure / Origin Port</span>
              </label>
              <button
                type="button"
                onClick={() => onSetPickMode(pickMode === 'origin' ? null : 'origin')}
                className={`text-[11px] px-2 py-0.5 rounded flex items-center space-x-1 transition-all cursor-pointer ${
                  pickMode === 'origin'
                    ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm shadow-emerald-500/50'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
                title="Click on the map to set origin"
              >
                <Crosshair className="w-3 h-3" />
                <span>{pickMode === 'origin' ? 'Click Map...' : 'Pick on Map'}</span>
              </button>
            </div>

            {/* Quick Port Selector */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowPortSearchOrigin(!showPortSearchOrigin)}
                className="w-full text-left px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-xs text-slate-300 flex items-center justify-between cursor-pointer"
              >
                <span className="truncate">Select from major ports...</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showPortSearchOrigin && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 max-h-48 overflow-y-auto">
                  <div className="p-1.5 sticky top-0 bg-slate-900 border-b border-slate-800">
                    <div className="flex items-center bg-slate-950 px-2 py-1 rounded border border-slate-800 text-xs">
                      <Search className="w-3 h-3 text-slate-400 mr-1.5 shrink-0" />
                      <input
                        type="text"
                        placeholder="Search port..."
                        value={originSearchQuery}
                        onChange={(e) => setOriginSearchQuery(e.target.value)}
                        className="bg-transparent border-none text-slate-200 focus:outline-none w-full"
                        autoFocus
                      />
                    </div>
                  </div>
                  {filteredOriginPorts.map((p) => (
                    <button
                      key={p.name}
                      type="button"
                      onClick={() => {
                        onOriginChange({ lon: p.lon, lat: p.lat });
                        setShowPortSearchOrigin(false);
                      }}
                      className="w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 flex items-center justify-between text-slate-300 cursor-pointer"
                    >
                      <span className="font-medium text-slate-200">{p.name}</span>
                      <span className="text-[10px] text-slate-500">{p.country}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Coordinate manual inputs */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[10px] text-slate-400 block mb-0.5">Lon (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={origin.lon}
                  onChange={(e) => onOriginChange({ ...origin, lon: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-0.5">Lat (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={origin.lat}
                  onChange={(e) => onOriginChange({ ...origin, lat: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Swap Button Divider */}
          <div className="flex items-center justify-center my-1">
            <button
              type="button"
              onClick={onSwapCoordinates}
              className="p-1 rounded-full bg-slate-800 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-700 hover:border-cyan-700 transition-colors cursor-pointer"
              title="Swap Origin and Destination"
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Destination Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center space-x-1.5 text-rose-400 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/30" />
                <span>Destination Port</span>
              </label>
              <button
                type="button"
                onClick={() => onSetPickMode(pickMode === 'destination' ? null : 'destination')}
                className={`text-[11px] px-2 py-0.5 rounded flex items-center space-x-1 transition-all cursor-pointer ${
                  pickMode === 'destination'
                    ? 'bg-rose-500 text-slate-950 font-semibold shadow-sm shadow-rose-500/50'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
                title="Click on the map to set destination"
              >
                <Crosshair className="w-3 h-3" />
                <span>{pickMode === 'destination' ? 'Click Map...' : 'Pick on Map'}</span>
              </button>
            </div>

            {/* Quick Port Selector */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowPortSearchDest(!showPortSearchDest)}
                className="w-full text-left px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-xs text-slate-300 flex items-center justify-between cursor-pointer"
              >
                <span className="truncate">Select from major ports...</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showPortSearchDest && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 max-h-48 overflow-y-auto">
                  <div className="p-1.5 sticky top-0 bg-slate-900 border-b border-slate-800">
                    <div className="flex items-center bg-slate-950 px-2 py-1 rounded border border-slate-800 text-xs">
                      <Search className="w-3 h-3 text-slate-400 mr-1.5 shrink-0" />
                      <input
                        type="text"
                        placeholder="Search port..."
                        value={destSearchQuery}
                        onChange={(e) => setDestSearchQuery(e.target.value)}
                        className="bg-transparent border-none text-slate-200 focus:outline-none w-full"
                        autoFocus
                      />
                    </div>
                  </div>
                  {filteredDestPorts.map((p) => (
                    <button
                      key={p.name}
                      type="button"
                      onClick={() => {
                        onDestinationChange({ lon: p.lon, lat: p.lat });
                        setShowPortSearchDest(false);
                      }}
                      className="w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 flex items-center justify-between text-slate-300 cursor-pointer"
                    >
                      <span className="font-medium text-slate-200">{p.name}</span>
                      <span className="text-[10px] text-slate-500">{p.country}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Coordinate manual inputs */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[10px] text-slate-400 block mb-0.5">Lon (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={destination.lon}
                  onChange={(e) => onDestinationChange({ ...destination, lon: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-0.5">Lat (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={destination.lat}
                  onChange={(e) => onDestinationChange({ ...destination, lat: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Preset Routes Carousel */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>Chokepoint Demo Routes</span>
            </span>
          </div>
          <div className="grid grid-cols-1 gap-1.5">
            {PRESET_ROUTES.map((pr) => (
              <button
                key={pr.id}
                type="button"
                onClick={() => handleSelectPreset(pr)}
                className="text-left p-2 rounded-lg bg-slate-950/50 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 transition-all group cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                    {pr.name}
                  </span>
                  <span className="text-[10px] text-cyan-400 bg-cyan-950/70 px-1.5 py-0.5 rounded border border-cyan-800/40">
                    Lvl {pr.level}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 truncate">
                  {pr.description}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Route Settings (Refinement Level & Layers) */}
        <div className="bg-slate-950/50 rounded-xl p-3 border border-slate-800 space-y-3">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <span>Refinement Resolution</span>
          </div>

          <div className="grid grid-cols-3 gap-1.5">
            {[
              { lvl: 1, label: 'Lvl 1', desc: 'Coarse' },
              { lvl: 2, label: 'Lvl 2', desc: 'Standard' },
              { lvl: 3, label: 'Lvl 3', desc: 'Ultra-Fine' },
            ].map((opt) => (
              <button
                key={opt.lvl}
                type="button"
                onClick={() => onRefinementLevelChange(opt.lvl)}
                className={`py-1.5 px-2 rounded-lg text-center transition-all cursor-pointer ${
                  refinementLevel === opt.lvl
                    ? 'bg-cyan-600 text-white font-semibold shadow-sm shadow-cyan-600/40'
                    : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <div className="text-xs">{opt.label}</div>
                <div className="text-[10px] opacity-75">{opt.desc}</div>
              </button>
            ))}
          </div>

          {/* Layer toggles */}
          <div className="pt-2 border-t border-slate-800/80 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="w-3 h-0.5 border-t-2 border-dashed border-amber-400 inline-block" />
                <span>Show Coarse Route</span>
              </span>
              <input
                type="checkbox"
                checked={showCoarseRoute}
                onChange={(e) => onToggleCoarseRoute(e.target.checked)}
                className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="w-3 h-1 bg-cyan-400 inline-block rounded" />
                <span>Show Refined Route</span>
              </span>
              <input
                type="checkbox"
                checked={showRefinedRoute}
                onChange={(e) => onToggleRefinedRoute(e.target.checked)}
                className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="w-2 h-2 rotate-45 bg-amber-400 inline-block" />
                <span>Show Chokepoints</span>
              </span>
              <input
                type="checkbox"
                checked={showChokepoints}
                onChange={(e) => onToggleChokepoints(e.target.checked)}
                className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Error message card */}
        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-800/80 text-rose-200 text-xs flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-semibold block">Routing Failure</span>
              <p className="text-[11px] leading-relaxed text-rose-300">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Action Button: Calculate Route */}
        <button
          type="button"
          onClick={onCalculateRoute}
          disabled={isLoading}
          className={`w-full py-3 px-4 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition-all shadow-lg cursor-pointer ${
            isLoading
              ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 shadow-cyan-500/25 active:scale-[0.98]'
          }`}
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              <span>Hierarchical Routing Computing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-slate-950" />
              <span>Calculate Shortest Maritime Route</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
