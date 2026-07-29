const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

// Auth API
export const auth = {
  register: (data: { email: string; name: string; password: string }) =>
    apiFetch<{ access_token: string; user: any }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    apiFetch<{ access_token: string; user: any }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Plans API
export const plans = {
  list: (token: string) =>
    apiFetch<any[]>('/api/plans', { token }),

  get: (token: string, id: string) =>
    apiFetch<any>(`/api/plans/${id}`, { token }),

  create: (token: string, data: { idea: string; title?: string; extra_info?: string }) =>
    apiFetch<any>('/api/plans', {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    }),

  generationStatus: (token: string, planId: string) =>
    apiFetch<any>(`/api/plans/${planId}/generation`, { token }),

  cancelGeneration: (token: string, planId: string) =>
    apiFetch<any>(`/api/plans/${planId}/generation/cancel`, {
      method: 'POST',
      token,
    }),

  resumeGeneration: (token: string, planId: string) =>
    apiFetch<any>(`/api/plans/${planId}/generation/resume`, {
      method: 'POST',
      token,
    }),

  delete: (token: string, id: string) =>
    apiFetch<void>(`/api/plans/${id}`, {
      method: 'DELETE',
      token,
    }),

  chat: (token: string, planId: string, message: string) =>
    apiFetch<any>(`/api/plans/${planId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message }),
      token,
    }),

  bootstrapValidationWorkspace: (token: string, planId: string) =>
    apiFetch<any>(`/api/plans/${planId}/validation-workspace/bootstrap`, {
      method: 'POST',
      token,
    }),

  refreshResearch: (token: string, planId: string) =>
    apiFetch<any>(`/api/plans/${planId}/research/refresh`, {
      method: 'POST',
      token,
    }),

  createAssumption: (token: string, planId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/assumptions`, {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    }),

  updateAssumption: (token: string, planId: string, itemId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/assumptions/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
      token,
    }),

  deleteAssumption: (token: string, planId: string, itemId: string) =>
    apiFetch<void>(`/api/plans/${planId}/assumptions/${itemId}`, {
      method: 'DELETE',
      token,
    }),

  createEvidence: (token: string, planId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/evidence`, {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    }),

  updateEvidence: (token: string, planId: string, itemId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/evidence/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
      token,
    }),

  deleteEvidence: (token: string, planId: string, itemId: string) =>
    apiFetch<void>(`/api/plans/${planId}/evidence/${itemId}`, {
      method: 'DELETE',
      token,
    }),

  createExperiment: (token: string, planId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/experiments`, {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    }),

  updateExperiment: (token: string, planId: string, itemId: string, data: any) =>
    apiFetch<any>(`/api/plans/${planId}/experiments/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
      token,
    }),

  deleteExperiment: (token: string, planId: string, itemId: string) =>
    apiFetch<void>(`/api/plans/${planId}/experiments/${itemId}`, {
      method: 'DELETE',
      token,
    }),
};
