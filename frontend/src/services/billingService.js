import apiClient from "../core/apiClient.js";

export async function getBillingStatus() {
  return apiClient.request("/billing/status", { method: "GET" });
}

export async function subscribePro() {
  const data = await apiClient.request("/billing/create-checkout-session", {
    method: "POST",
    redirectOnAuthError: false,
  });

  return {
    checkout_url: data?.checkout_url || data?.url || null,
    url: data?.url || data?.checkout_url || null,
  };
}

export async function cancelSubscription() {
  return apiClient.request("/billing/cancel-subscription", {
    method: "POST",
  });
}

export async function openCustomerPortal() {
  const data = await apiClient.request("/billing/create-portal-session", {
    method: "POST",
  });

  return {
    portal_url: data?.portal_url || data?.url || null,
    url: data?.url || data?.portal_url || null,
  };
}