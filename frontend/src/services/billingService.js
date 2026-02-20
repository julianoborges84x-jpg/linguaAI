import apiClient from "../core/apiClient.js";

export async function subscribePro() {
  return apiClient.request("/create-checkout-session", { method: "POST" });
}

export async function cancelSubscription() {
  return apiClient.request("/cancel-subscription", { method: "POST" });
}

export async function openCustomerPortal() {
  return apiClient.request("/customer-portal", { method: "POST" });
}
