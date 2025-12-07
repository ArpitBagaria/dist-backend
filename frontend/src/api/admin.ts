import api from "./client";

export async function uploadPrices(formData: FormData) {
  return (await api.post("/admin/products/prices", formData)).data;
}
