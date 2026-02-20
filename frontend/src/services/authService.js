import apiClient from "../core/apiClient.js";
import storage from "../core/storage.js";

function parseUserId(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub;
  } catch {
    return null;
  }
}

export async function login(email, password) {
  const data = await apiClient.request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
  storage.set("auth_token", data.access_token);
  return data;
}

export async function register(payload) {
  return apiClient.request("/users", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function logout() {
  storage.remove("auth_token");
}

export function getToken() {
  return storage.get("auth_token");
}

export function getUserIdFromToken() {
  const token = storage.get("auth_token");
  return token ? parseUserId(token) : null;
}
