import apiClient from "../core/apiClient.js";

export async function getDailyMessage() {
  return apiClient.request("/daily-message/today");
}

export async function getStreak() {
  return apiClient.request("/daily-message/streak");
}
