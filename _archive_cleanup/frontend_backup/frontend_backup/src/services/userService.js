import api from "../core/apiClient.js";

// Perfil do usuário logado
export async function getCurrentUser() {
  return await api.request("/users/me", { method: "GET" });
}

// Atualizar dados do usuário logado
export async function updateUser(payload) {
  return await api.request("/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function getUserPreferences() {
  return await api.request("/users/preferences", { method: "GET" });
}

export async function updateUserPreferences(payload) {
  return await api.request("/users/preferences", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function completeOnboarding(payload) {
  return await api.request("/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
