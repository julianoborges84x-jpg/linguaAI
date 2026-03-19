import apiClient from "../core/apiClient.js";

export async function sendChatMessage(message) {
  return apiClient.request("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export async function getTopics() {
  return apiClient.request("/topics");
}

export async function getHistory() {
  return apiClient.request("/history");
}

export async function getVocabulary() {
  return apiClient.request("/vocabulary");
}

export async function getProgress() {
  return apiClient.request("/progress");
}

export async function updateProgress(payload) {
  return apiClient.request("/progress", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function getProgressSummary() {
  return apiClient.request("/progress/summary");
}

export async function startStudySession(mode, topic_id = null) {
  return apiClient.request("/sessions/start", {
    method: "POST",
    body: JSON.stringify({ mode, topic_id }),
  });
}

export async function finishStudySession(sessionId, interactions_count = null) {
  return apiClient.request(`/sessions/${sessionId}/finish`, {
    method: "POST",
    body: JSON.stringify({ interactions_count }),
  });
}
