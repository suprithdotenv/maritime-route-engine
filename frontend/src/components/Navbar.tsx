import React from 'react';
import { Compass, ExternalLink, Anchor } from 'lucide-react';
import type { SystemHealth } from '../types';
import { CHOKEPOINTS } from '../data/chokepoints';

interface NavbarProps {
  health: SystemHealth | null;
  healthLoading: boolean;
  onSelectChokepoint: (lon: number, lat: number, zoom: number) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  healthLoading,
  onSelectChokepoint,
}) => {
  return (
    <header className="h-14 bg-slate-900/95 backdrop-blur border-b border-slate-800 text-slate-100 flex items-center justify-between px-4 z-30 shrink-0">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
          <Compass className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-base tracking-wide bg-gradient-to-r from-white via-slate-100 to-cyan-200 bg-clip-text text-transparent">
              VoyageIQ
            </h1>
            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 uppercase tracking-wider">
              MVP 1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            Hierarchical Maritime Routing & Narrow Chokepoint Engine
          </p>
        </div>
      </div>

      {/* Middle: Strait Quick Jumps */}
      <div className="hidden lg:flex items-center space-x-1.5 bg-slate-950/60 p-1 rounded-lg border border-slate-800/80 text-xs text-slate-300">
        <div className="flex items-center px-2 py-0.5 text-slate-400 text-[11px] font-medium border-r border-slate-800 mr-1">
          <Anchor className="w-3.5 h-3.5 mr-1 text-cyan-400" />
          <span>Chokepoints:</span>
        </div>
        {CHOKEPOINTS.slice(0, 5).map((cp) => (
          <button
            key={cp.id}
            onClick={() => onSelectChokepoint(cp.lon, cp.lat, cp.zoom)}
            className="px-2 py-1 rounded hover:bg-slate-800 hover:text-cyan-300 transition-colors text-slate-300 font-medium"
            title={cp.description}
          >
            {cp.name}
          </button>
        ))}
      </div>

      {/* Right side: System Health & Docs */}
      <div className="flex items-center space-x-3">
        {/* Health status pill */}
        <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-950/70 border border-slate-800 text-xs">
          {healthLoading ? (
            <>
              <div className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span className="text-slate-400">Connecting...</span>
            </>
          ) : health && health.status === 'healthy' ? (
            <>
              <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/80" />
              <span className="text-emerald-400 font-medium hidden sm:inline">Backend Online</span>
              <span className="text-slate-500 text-[11px] hidden md:inline">
                ({health.features_count.toLocaleString()} polygons)
              </span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 rounded-full bg-rose-500" />
              <span className="text-rose-400 font-medium">Backend Offline</span>
            </>
          )}
        </div>

        {/* API Docs Button */}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-1 px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors border border-slate-700"
          title="Open FastAPI Swagger Interactive Documentation"
        >
          <span className="hidden sm:inline">FastAPI Docs</span>
          <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
        </a>
      </div>
    </header>
  );
};
