const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const TOKEN_KEY = 'token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

type ApiRequestOptions = RequestInit & {
  authenticated?: boolean;
  isForm?: boolean;
};

export async function apiRequest<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
  const { authenticated = false, isForm = false, headers, body, ...rest } = options;
  const token = getToken();
  const finalHeaders = new Headers(headers);

  if (!isForm && !finalHeaders.has('Content-Type') && body !== undefined) {
    finalHeaders.set('Content-Type', 'application/json');
  }

  if (authenticated && token) {
    finalHeaders.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...rest,
    headers: finalHeaders,
    body,
  });

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    const message =
      (data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string' && data.detail) ||
      'API request failed';
    throw new Error(message);
  }

  return data as T;
}

export { API_URL, TOKEN_KEY };
