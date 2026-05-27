import { apiRequest } from "./apiClient.js";

export async function listOrders(params = {}) {
  const qs = new URLSearchParams();
  if (params.orderId) qs.set("order_id", String(params.orderId));
  if (params.date) qs.set("date", params.date);
  const suffix = qs.toString();
  const endpoint = suffix ? `/orders?${suffix}` : "/orders";
  return apiRequest(endpoint);
}

export async function getOrder(orderId) {
  return apiRequest(`/orders/${orderId}`);
}

export async function createOrder(body) {
  return apiRequest("/orders", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function patchOrderStatus(orderId, status) {
  return apiRequest(`/orders/${orderId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function updateSavedOrder(orderId, body) {
  return apiRequest(`/orders/${orderId}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}
