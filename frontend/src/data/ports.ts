import type { PortPreset } from '../types';

export const MAJOR_PORTS: PortPreset[] = [
  { name: 'Mumbai (JNPT)', country: 'India', lon: 72.85, lat: 18.95, region: 'Indian Ocean' },
  { name: 'Alexandria Harbor', country: 'Egypt', lon: 29.90, lat: 31.20, region: 'Mediterranean' },
  { name: 'Singapore', country: 'Singapore', lon: 103.85, lat: 1.25, region: 'Southeast Asia' },
  { name: 'Rotterdam', country: 'Netherlands', lon: 4.30, lat: 51.95, region: 'North Europe' },
  { name: 'Shanghai (Yangshan)', country: 'China', lon: 121.90, lat: 30.60, region: 'East Asia' },
  { name: 'Dubai (Jebel Ali)', country: 'United Arab Emirates', lon: 55.05, lat: 25.00, region: 'Middle East' },
  { name: 'Tokyo / Yokohama', country: 'Japan', lon: 139.68, lat: 35.40, region: 'East Asia' },
  { name: 'Hamburg', country: 'Germany', lon: 9.85, lat: 53.55, region: 'North Europe' },
  { name: 'Antwerp', country: 'Belgium', lon: 4.30, lat: 51.28, region: 'North Europe' },
  { name: 'Hong Kong', country: 'Hong Kong', lon: 114.15, lat: 22.30, region: 'East Asia' },
  { name: 'Busan', country: 'South Korea', lon: 129.08, lat: 35.10, region: 'East Asia' },
  { name: 'Jeddah Islamic Port', country: 'Saudi Arabia', lon: 39.15, lat: 21.48, region: 'Red Sea' },
  { name: 'Piraeus (Athens)', country: 'Greece', lon: 23.63, lat: 37.94, region: 'Mediterranean' },
  { name: 'Colombo', country: 'Sri Lanka', lon: 79.84, lat: 6.94, region: 'Indian Ocean' },
  { name: 'Cape Town', country: 'South Africa', lon: 18.44, lat: -33.90, region: 'South Atlantic' },
  { name: 'Port Said (Suez North)', country: 'Egypt', lon: 32.31, lat: 31.26, region: 'Suez Canal' },
  { name: 'Suez Port (Suez South)', country: 'Egypt', lon: 32.55, lat: 29.92, region: 'Suez Canal' },
  { name: 'Gibraltar Port', country: 'Gibraltar', lon: -5.35, lat: 36.14, region: 'Strait of Gibraltar' },
  { name: 'Dover Port', country: 'United Kingdom', lon: 1.34, lat: 51.12, region: 'English Channel' },
  { name: 'New York / New Jersey', country: 'USA', lon: -74.05, lat: 40.65, region: 'North America East' },
  { name: 'Los Angeles / Long Beach', country: 'USA', lon: -118.25, lat: 33.74, region: 'North America West' },
  { name: 'Santos', country: 'Brazil', lon: -46.30, lat: -23.95, region: 'South America East' },
  { name: 'Sydney Port Jackson', country: 'Australia', lon: 151.25, lat: -33.85, region: 'Oceania' },
  { name: 'Panama (Balboa - Pacific)', country: 'Panama', lon: -79.52, lat: 8.90, region: 'Central America' },
  { name: 'Panama (Colon - Caribbean)', country: 'Panama', lon: -79.92, lat: 9.35, region: 'Central America' },
];

export interface PresetRoute {
  id: string;
  name: string;
  description: string;
  origin: PortPreset;
  destination: PortPreset;
  level: number;
}

export const PRESET_ROUTES: PresetRoute[] = [
  {
    id: 'suez-corridor',
    name: 'Mumbai → Alexandria',
    description: 'Direct transit through Bab-el-Mandeb & Suez Canal',
    origin: MAJOR_PORTS[0], // Mumbai
    destination: MAJOR_PORTS[1], // Alexandria
    level: 2
  },
  {
    id: 'east-west-trunk',
    name: 'Singapore → Rotterdam',
    description: 'Major global trade trunk via Malacca, Suez, and Dover',
    origin: MAJOR_PORTS[2], // Singapore
    destination: MAJOR_PORTS[3], // Rotterdam
    level: 2
  },
  {
    id: 'hormuz-energy',
    name: 'Dubai → Tokyo',
    description: 'Crude tanker route out of Persian Gulf via Hormuz & Malacca',
    origin: MAJOR_PORTS[5], // Dubai
    destination: MAJOR_PORTS[6], // Tokyo
    level: 2
  },
  {
    id: 'atlantic-med',
    name: 'New York → Piraeus',
    description: 'Transatlantic corridor entering Mediterranean via Gibraltar',
    origin: MAJOR_PORTS[19], // NY
    destination: MAJOR_PORTS[12], // Piraeus
    level: 2
  },
  {
    id: 'panama-demo',
    name: 'Colon → Balboa (Panama Demo)',
    description: 'Demonstrates limitation reporting for freshwater lock gap',
    origin: MAJOR_PORTS[24], // Colon
    destination: MAJOR_PORTS[23], // Balboa
    level: 1
  }
];
