import type { ChokepointLocation } from '../types';

export const CHOKEPOINTS: ChokepointLocation[] = [
  {
    id: 'suez',
    name: 'Suez Canal',
    lon: 32.34,
    lat: 30.55,
    zoom: 9,
    description: '193 km artificial sea-level waterway connecting Mediterranean Sea to Red Sea. Fully resolved in ocean polygons.',
    supported: true
  },
  {
    id: 'bab_el_mandeb',
    name: 'Bab-el-Mandeb Strait',
    lon: 43.35,
    lat: 12.65,
    zoom: 9,
    description: 'Narrow strait connecting the Red Sea to the Gulf of Aden / Arabian Sea between Yemen and Djibouti.',
    supported: true
  },
  {
    id: 'hormuz',
    name: 'Strait of Hormuz',
    lon: 56.40,
    lat: 26.50,
    zoom: 9,
    description: 'Strategic chokepoint between Oman and Iran connecting Persian Gulf to Arabian Sea.',
    supported: true
  },
  {
    id: 'malacca',
    name: 'Strait of Malacca & Singapore',
    lon: 102.50,
    lat: 2.20,
    zoom: 8,
    description: 'Critical maritime corridor connecting Andaman Sea / Indian Ocean to South China Sea / Pacific.',
    supported: true
  },
  {
    id: 'gibraltar',
    name: 'Strait of Gibraltar',
    lon: -5.60,
    lat: 35.95,
    zoom: 10,
    description: 'Narrow strait connecting Atlantic Ocean to Mediterranean Sea between Spain and Morocco.',
    supported: true
  },
  {
    id: 'dover',
    name: 'Strait of Dover / English Channel',
    lon: 1.45,
    lat: 51.10,
    zoom: 9,
    description: 'Busiest shipping lane in the world connecting English Channel to North Sea.',
    supported: true
  },
  {
    id: 'panama',
    name: 'Panama Canal (Limitation)',
    lon: -79.70,
    lat: 9.10,
    zoom: 10,
    description: 'Freshwater lock system through Gatun Lake. Omitted in ocean polygon dataset; reported as coverage limitation.',
    supported: false
  }
];
