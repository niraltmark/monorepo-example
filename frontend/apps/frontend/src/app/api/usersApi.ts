const BASE_URL = import.meta.env.VITE_USERS_SERVICE_URL ?? 'http://localhost:8001/api/v1';

export interface UserRead {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const usersApi = {
  register: (payload: RegisterPayload) =>
    request<UserRead>('/users/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  login: (payload: LoginPayload) =>
    request<TokenResponse>('/users/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getMe: (token: string) =>
    request<UserRead>('/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
};
