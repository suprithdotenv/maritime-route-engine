import type { RouteRequest, RouteResponse, SystemHealth } from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export async function fetchHealth(): Promise<SystemHealth> {
  const url = `${API_BASE}/api/health`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Health check failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function computeRoute(
  request: RouteRequest,
  useDebugEndpoint: boolean = true
): Promise<RouteResponse> {
  const endpoint = useDebugEndpoint ? '/api/route/debug' : '/api/route';
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMsg = `Server error HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return response.json();
}
