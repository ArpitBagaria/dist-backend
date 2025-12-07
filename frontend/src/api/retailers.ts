import api from "./client";

export async function getRetailers() {
  const res = await api.get("/retailers");
  return res.data;
}

export async function getNegativeReport() {
  const res = await api.get("/reports/negative");
  return res.data;
}
