import { ENV } from "../config/env.js";
import storage from "./storage.js";

function normalizeError(detail) {
  // FastAPI costuma retornar detail como array de objetos:
  // [{loc:..., msg:"Field required", type:...}, ...]
  if (Array.isArray(detail)) {
    return detail
      .map((e) => {
        const where = Array.isArray(e.loc) ? e.loc.join(".") : "";
        const msg = e.msg || JSON.stringify(e);
        return where ? `${where}: ${msg}` : msg;
      })
      .join(" | ");
  }
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") return detail.msg || JSON.stringify(detail);
  return "Erro inesperado";
}

async function request(path, options = {}) {
  const base = (ENV.API_URL || "").replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  const url = `${base}${p}`;
  const method = (options.method || "GET").toUpperCase();

  const headers = { ...(options.headers || {}) };

  const isFormData = options.body instanceof FormData;
  const hasContentType = Object.keys(headers).some(
    (k) => k.toLowerCase() === "content-type"
  );
  if (!isFormData && options.body !== undefined && !hasContentType) {
    headers["Content-Type"] = "application/json";
  }

  const token = storage.get("auth_token");
  if (token) headers.Authorization = `Bearer ${token}`;

  console.debug("[apiClient.request] ->", { url, method });
  const res = await fetch(url, { ...options, headers });
  console.debug("[apiClient.request] <-", { url, method, status: res.status });

  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text || null;
  }

  if (!res.ok) {
    const shouldRedirectOnAuthError = options.redirectOnAuthError !== false;
    if (res.status === 401) {
      storage.remove("auth_token");
      if (
        shouldRedirectOnAuthError &&
        typeof window !== "undefined" &&
        window.location.pathname !== "/login"
      ) {
        window.location.href = "/login";
      }
    }

    const detail =
      (data && (data.detail ?? data.message ?? data.error)) ||
      `Erro HTTP ${res.status}`;

    throw new Error(normalizeError(detail));
  }

  return data;
}

export default { request };
export { request };
