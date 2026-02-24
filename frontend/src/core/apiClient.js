import { ENV } from "../config/env.js";
import storage from "./storage.js";

async function request(path, options = {}) {
  const url = `${ENV.API_URL}${path.startsWith("/") ? path : `/${path}`}`;

  const headers = {
    ...(options.headers || {}),
  };

  // Só seta Content-Type se NÃO for FormData
  const isFormData = options.body instanceof FormData;
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const token = storage.get("auth_token");
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });

  // tenta ler json, mas sem quebrar se vier vazio
  const payload = await res.text();
  const data = payload ? JSON.parse(payload) : null;

  if (!res.ok) {
    const detail =
      (data && (data.detail || data.message)) ||
      `Erro HTTP ${res.status}`;
    throw new Error(detail);
  }

  return data;
}

export default { request };