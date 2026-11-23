export interface Coordinate {
  lon: number;
  lat: number;
}

export interface RouteRequest {
  origin: Coordinate;
  destination: Coordinate;
  refinement_level: number;
}

export interface ValidationReport {
  is_valid: boolean;
  total_distance_km: number;
  segment_count: number;
  invalid_segments: any[];
  error: string | null;
}

export interface RouteDebugData {
  coarse_route: [number, number][];
  coarse_distance_km: number;
  refined_route: [number, number][];
  global_nodes_count: number;
  global_edges_count: number;
  regional_nodes_count: number;
  regional_edges_count: number;
  validation_report: ValidationReport;
  computation_time_ms: number;
  narrow_passages_preserved: string[];
}

export interface RouteResponse {
  route_found: boolean;
  coordinates: [number, number][]; // [lon, lat]
  total_distance_km: number;
  global_nodes_count: number;
  global_edges_count: number;
  regional_nodes_count: number;
  regional_edges_count: number;
  refinement_level_reached: number;
  traversed_chokepoints: string[];
  warnings: string[];
  error_detail: string | null;
  debug?: RouteDebugData;
}

export interface SystemHealth {
  status: string;
  data_loaded: boolean;
  features_count: number;
  graph_loaded: boolean;
  graph_nodes: number;
  graph_edges: number;
  supported_chokepoints: string[];
  unsupported_chokepoints: string[];
}

export interface PortPreset {
  name: string;
  country: string;
  lon: number;
  lat: number;
  region: string;
}

export interface ChokepointLocation {
  id: string;
  name: string;
  lon: number;
  lat: number;
  zoom: number;
  description: string;
  supported: boolean;
}
