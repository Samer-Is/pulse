/**
 * Shared TypeScript types for Pulse AI Studio
 */

export interface User {
  id: string;
  email: string;
  name: string;
  authProvider: 'google';
  isAdmin: boolean;
  createdAt: string;
}

export interface Plan {
  id: string;
  name: string;
  monthlyPriceJod: number;
  chatTokens: number;
  imageCreations: number;
  videoSeconds: number;
  cvExports: number;
  slideExports: number;
  isActive: boolean;
}

export interface Subscription {
  id: string;
  userId: string;
  planId: string;
  status: 'pending' | 'active' | 'cancelled' | 'expired';
  periodStart: string;
  periodEnd: string;
  paymentMethod: 'manual' | 'paypal' | 'hyperpay';
  manualVerifiedBy?: string;
}

export interface UsageEvent {
  id: string;
  userId: string;
  feature: 'chat' | 'image' | 'video' | 'cv' | 'slide';
  model?: string;
  inputTokens?: number;
  outputTokens?: number;
  imageCount?: number;
  videoSeconds?: number;
  bytes?: number;
  costEstimate?: number;
  createdAt: string;
}

export interface Job {
  id: string;
  userId: string;
  type: 'video' | 'image' | 'cv' | 'slide';
  payloadJson: Record<string, unknown>;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  resultUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export type ChatProvider = 'openai' | 'anthropic' | 'google';
export type ImageProvider = 'google' | 'openai';
export type VideoProvider = 'runway' | 'pika';

