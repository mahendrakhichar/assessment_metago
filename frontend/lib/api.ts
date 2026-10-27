/**
 * API client — typed fetch wrapper for the Metago backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

let accessToken: string | null = null;

export function setAccessToken(token: string) {
  accessToken = token;
}

export function clearAccessToken() {
  accessToken = null;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(error.detail || 'Request failed', response.status, error.detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

// ── Auth ─────────────────────────────────────────────────────────
export const auth = {
  login: (email: string, password: string) =>
    request<{ access_token: string; refresh_token: string; user: User }>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: undefined,
      // Override for form encoding
    }).then(() => {
      // Use native fetch for form-encoded login
      const form = new URLSearchParams({ username: email, password });
      return fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
      }).then((r) => r.json());
    }),

  me: () => request<User>('/auth/me'),
  register: (data: { email: string; full_name: string; password: string }) =>
    request<User>('/auth/register', { method: 'POST', body: data }),
};

// ── Analytics ───────────────────────────────────────────────────
export const analytics = {
  overview: () => request<OverviewStats>('/analytics/overview'),
};

// ── Content ─────────────────────────────────────────────────────
export const content = {
  pillars: () => request<ContentPillar[]>('/content/pillars'),
  ideas: (status?: string) =>
    request<ContentIdea[]>(`/content/ideas${status ? `?status=${status}` : ''}`),
  assets: (status?: string) =>
    request<CanonicalAsset[]>(`/content/assets${status ? `?status=${status}` : ''}`),
  getAsset: (id: string) => request<CanonicalAsset>(`/content/assets/${id}`),
};

// ── Trends ──────────────────────────────────────────────────────
export const trends = {
  topics: (isTrending?: boolean) =>
    request<Topic[]>(`/trends/topics${isTrending !== undefined ? `?is_trending=${isTrending}` : ''}`),
};

// ── Accounts ────────────────────────────────────────────────────
export const accounts = {
  list: () => request<SocialAccount[]>('/accounts/'),
};

// ── Publishing ───────────────────────────────────────────────────
export const publishing = {
  schedules: (status?: string) =>
    request<Schedule[]>(`/publishing/schedules${status ? `?status=${status}` : ''}`),
  createSchedule: (data: {
    variant_id: string;
    account_id: string;
    scheduled_for: string;
    idempotency_key?: string;
  }) => request<Schedule>('/publishing/schedules', { method: 'POST', body: data }),
  mockPublish: (scheduleId: string) =>
    request<PublishedPost>(`/publishing/schedules/${scheduleId}/publish`, { method: 'POST' }),
  posts: (accountId?: string) =>
    request<PublishedPost[]>(`/publishing/posts${accountId ? `?account_id=${accountId}` : ''}`),
};

// ── Types ────────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface OverviewStats {
  total_assets: number;
  published_assets: number;
  pending_review: number;
  total_posts: number;
  connected_accounts: number;
}

export interface ContentPillar {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  sort_order: number;
  created_at: string;
}

export interface ContentIdea {
  id: string;
  title: string;
  description: string | null;
  priority_score: number;
  status: string;
  audience: string | null;
  funnel_stage: string | null;
  created_by_agent: boolean;
  created_at: string;
}

export interface CanonicalAsset {
  id: string;
  title: string;
  body: string;
  summary: string | null;
  language: string;
  medical_risk: string;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Topic {
  id: string;
  title: string;
  slug: string;
  category: string | null;
  is_evergreen: boolean;
  is_trending: boolean;
  medical_risk: string;
  final_score: number;
  audience_relevance: number;
  created_at: string;
}

export interface SocialAccount {
  id: string;
  platform: string;
  account_name: string;
  display_name: string | null;
  is_active: boolean;
  is_paused: boolean;
  is_mock: boolean;
  health_status: string;
  follower_count: number | null;
  created_at: string;
}

export interface Schedule {
  id: string;
  platform_variant_id: string;
  account_id: string;
  scheduled_for: string;
  status: string;
  idempotency_key: string;
  notes: string | null;
  created_at: string;
}

export interface PublishedPost {
  id: string;
  schedule_id: string | null;
  platform_variant_id: string;
  account_id: string;
  platform_post_id: string | null;
  platform_post_url: string | null;
  published_at: string;
  is_mock: boolean;
  created_at: string;
}
