function resolveApiUrl() {
  const fromEnv = (import.meta.env.VITE_API_URL || '').trim();

  // ✅ PRIORIDADE TOTAL: variável da Vercel
  if (fromEnv) {
    return fromEnv.replace(/\/$/, '');
  }

  // 🔒 BLOQUEIO EM PRODUÇÃO (EVITA USAR LOCALHOST SEM QUERER)
  if (typeof window !== 'undefined') {
    const host = window.location.hostname.toLowerCase();
    const isLocal = host === 'localhost' || host === '127.0.0.1';

    if (!isLocal) {
      throw new Error(
        '❌ VITE_API_URL NÃO CONFIGURADO EM PRODUÇÃO. Configure na Vercel.'
      );
    }

    // 🧪 Ambiente local
    return 'http://127.0.0.1:8000';
  }

  // fallback extremo (SSR ou erro raro)
  return 'http://127.0.0.1:8000';
}

const API_URL = resolveApiUrl();
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

export async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    authenticated = false,
    isForm = false,
    headers,
    body,
    ...rest
  } = options;

  const token = getToken();
  const finalHeaders = new Headers(headers);

  // JSON automático
  if (!isForm && !finalHeaders.has('Content-Type') && body !== undefined) {
    finalHeaders.set('Content-Type', 'application/json');
  }

  // Auth
  if (authenticated && token) {
    finalHeaders.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...rest,
    headers: finalHeaders,
    body,
  });

  const isJson = response.headers
    .get('content-type')
    ?.includes('application/json');

  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    const message =
      (data &&
        typeof data === 'object' &&
        'detail' in data &&
        typeof data.detail === 'string' &&
        data.detail) ||
      `Erro ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}

export { API_URL, TOKEN_KEY };