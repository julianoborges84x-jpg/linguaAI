import api from "../core/apiClient.js";
import storage from "../core/storage.js";

const TOKEN_KEY = "auth_token";

export function getToken() {
  return storage.get(TOKEN_KEY);
}

export function setToken(token) {
  storage.set(TOKEN_KEY, token);
}

export function logout() {
  storage.remove(TOKEN_KEY);
}

export async function login(email, password) {
  // backend: POST /auth/login (OAuth2 form)
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const data = await api.request("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  // aceita formatos comuns:
  const token = data?.access_token || data?.token || data?.jwt;
  if (!token) throw new Error("Login não retornou token.");

  setToken(token);
  return data;
}

export async function register({ name, email, password }) {
  // backend: POST /users
  const payload = { name, email, password };

  const data = await api.request("/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return data;
}
