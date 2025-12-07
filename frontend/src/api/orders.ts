import api from "./client";

export async function autoApproval(payload: any) {
  return (await api.post("/orders/auto-approval", payload)).data;
}

export async function createOrder(payload: any) {
  return (await api.post("/orders", payload)).data;
}

export async function getOrders(params = {}) {
  return (await api.get("/orders", { params })).data;
}

export async function getOrder(id: number) {
  return (await api.get(`/orders/${id}`)).data;
}

export async function updateOrderStatus(id: number, body: any) {
  return (await api.patch(`/orders/${id}/status`, body)).data;
}
