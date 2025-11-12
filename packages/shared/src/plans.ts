/**
 * Plan definitions for Pulse AI Studio
 * These will be seeded into the database
 */

import { Plan } from './types';

export const PLANS: Omit<Plan, 'id'>[] = [
  {
    name: 'Starter',
    monthlyPriceJod: 3,
    chatTokens: 50000,
    imageCreations: 20,
    videoSeconds: 30,
    cvExports: 1,
    slideExports: 1,
    isActive: true,
  },
  {
    name: 'Plus',
    monthlyPriceJod: 4,
    chatTokens: 150000,
    imageCreations: 50,
    videoSeconds: 90,
    cvExports: 5,
    slideExports: 5,
    isActive: true,
  },
  {
    name: 'Pro',
    monthlyPriceJod: 5,
    chatTokens: 300000,
    imageCreations: 100,
    videoSeconds: 180,
    cvExports: 20,
    slideExports: 20,
    isActive: true,
  },
];

