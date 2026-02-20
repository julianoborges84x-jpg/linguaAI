import apiClient from "../core/apiClient.js";
import { getUserIdFromToken } from "./authService.js";

export async function getCurrentUser() {
  const id = getUserIdFromToken();
  if (!id) return null;
  return apiClient.request(`/users/${id}`);
}

export async function updateUser(id, payload) {
  return apiClient.request(`/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
