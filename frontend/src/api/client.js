import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "https://fairmindai-production.up.railway.app";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
});

/** POST /api/scan — upload CSV and run fairness audit */
export async function scanDataset(formData) {
  const res = await api.post("/api/scan", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function getExplanation(auditId, mode = "professional", auditResults = null) {
  const res = await api.post("/api/explain", { audit_id: auditId, mode, audit_results: auditResults });
  return res.data;
}

/** POST /api/simulate — run mitigation simulation */
export async function runSimulation(formData) {
  const res = await api.post("/api/simulate", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

/** GET /api/report/{id} — download audit report */
export async function getReport(auditId) {
  const res = await api.get(`/api/report/${auditId}`);
  return res.data;
}

export async function downloadReport(auditId) {
  const res = await api.get(`/api/report/${auditId}?fmt=download`, {
    responseType: "blob",
  });
  return res.data;
}

/** GET /api/reports — list recent audits */
export async function listReports() {
  const res = await api.get("/api/reports");
  return res.data;
}
