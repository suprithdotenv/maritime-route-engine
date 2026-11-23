import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { RouteSidebar } from './components/RouteSidebar';
import { MapComponent } from './components/MapComponent';
import { RouteResults } from './components/RouteResults';
import type { Coordinate, RouteResponse, SystemHealth } from './types';
import { computeRoute, fetchHealth } from './services/api';
import { MAJOR_PORTS } from './data/ports';

export function App() {
  // Default: Mumbai to Alexandria (via Suez)
  const [origin, setOrigin] = useState<Coordinate>({
    lon: MAJOR_PORTS[0].lon,
    lat: MAJOR_PORTS[0].lat,
  });
  const [destination, setDestination] = useState<Coordinate>({
    lon: MAJOR_PORTS[1].lon,
    lat: MAJOR_PORTS[1].lat,
  });

  const [refinementLevel, setRefinementLevel] = useState<number>(2);
  const [pickMode, setPickMode] = useState<'origin' | 'destination' | null>(null);

  // Layer Visibility
  const [showCoarseRoute, setShowCoarseRoute] = useState<boolean>(true);
  const [showRefinedRoute, setShowRefinedRoute] = useState<boolean>(true);
  const [showChokepoints, setShowChokepoints] = useState<boolean>(true);

  // Routing State
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // System Health
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  // Map Target View
  const [targetView, setTargetView] = useState<{ lon: number; lat: number; zoom: number } | null>(null);

  // Poll health on mount
  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const h = await fetchHealth();
        if (isMounted) {
          setHealth(h);
          setHealthLoading(false);
        }
      } catch (e) {
        if (isMounted) {
          setHealthLoading(false);
        }
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Compute Maritime Route
  const handleCalculateRoute = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    setPickMode(null);

    try {
      const result = await computeRoute({
        origin,
        destination,
        refinement_level: refinementLevel,
      });

      if (!result.route_found) {
        setErrorMessage(
          result.error_detail ||
          'No valid navigable maritime route could be computed between the selected coordinates. The departure or destination may be in deep inland territory or separated by land.'
        );
        setRoute(null);
      } else {
        setRoute(result);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred while communicating with the routing engine.');
      setRoute(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwapCoordinates = () => {
    const temp = { ...origin };
    setOrigin(destination);
    setDestination(temp);
    // Invalidate old route until recalculated
    setRoute(null);
  };

  const handleClearRoute = () => {
    setRoute(null);
    setErrorMessage(null);
    setPickMode(null);
  };

  const handleMapClick = (coord: Coordinate) => {
    if (pickMode === 'origin') {
      setOrigin(coord);
      setRoute(null);
    } else if (pickMode === 'destination') {
      setDestination(coord);
      setRoute(null);
    }
    setPickMode(null);
  };

  const handleSelectChokepoint = (lon: number, lat: number, zoom: number) => {
    setTargetView({ lon, lat, zoom });
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* Top Navigation Bar */}
      <Navbar
        health={health}
        healthLoading={healthLoading}
        onSelectChokepoint={handleSelectChokepoint}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 relative overflow-hidden">
        {/* Left Floating / Fixed Route Sidebar */}
        <RouteSidebar
          origin={origin}
          destination={destination}
          onOriginChange={(c) => { setOrigin(c); setRoute(null); }}
          onDestinationChange={(c) => { setDestination(c); setRoute(null); }}
          onSwapCoordinates={handleSwapCoordinates}
          pickMode={pickMode}
          onSetPickMode={setPickMode}
          refinementLevel={refinementLevel}
          onRefinementLevelChange={(lvl) => setRefinementLevel(lvl)}
          showCoarseRoute={showCoarseRoute}
          onToggleCoarseRoute={setShowCoarseRoute}
          showRefinedRoute={showRefinedRoute}
          onToggleRefinedRoute={setShowRefinedRoute}
          showChokepoints={showChokepoints}
          onToggleChokepoints={setShowChokepoints}
          onCalculateRoute={handleCalculateRoute}
          onClearRoute={handleClearRoute}
          isLoading={isLoading}
          hasRoute={!!route}
          errorMessage={errorMessage}
        />

        {/* Map Canvas */}
        <main className="flex-1 relative h-full w-full">
          <MapComponent
            origin={origin}
            destination={destination}
            route={route}
            pickMode={pickMode}
            onMapClick={handleMapClick}
            showCoarseRoute={showCoarseRoute}
            showRefinedRoute={showRefinedRoute}
            showChokepoints={showChokepoints}
            targetView={targetView}
          />

          {/* Floating Route Results Panel (Top Right over map) */}
          {route && (
            <div className="absolute top-4 right-4 z-20 transition-all animate-in fade-in slide-in-from-top-4 duration-300">
              <RouteResults
                route={route}
                origin={origin}
                destination={destination}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
