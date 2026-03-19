import apiClient from "../core/apiClient.js";

export async function chatMentor(message, feature) {
  return apiClient.request("/mentor/chat", {
    method: "POST",
    body: JSON.stringify({ message, feature })
  });
}

export async function detectBaseLanguage(text) {
  return apiClient.request("/mentor/detect-language", {
    method: "POST",
    body: JSON.stringify({ text })
  });
}

export async function getMentorHistory() {
  return apiClient.request("/mentor/history");
}

export async function getWeeklyProgress() {
  return apiClient.request("/mentor/progress/weekly");
}
