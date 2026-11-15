/**
 * API boundary for the Python analytics service.
 * Set VITE_API_BASE_URL when the FastAPI service is ready.
 * The UI currently uses clearly-labelled demo data until an API is connected.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function uploadDataset(file: File) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_BASE}/api/datasets/upload`, { method: "POST", body });
  if (!response.ok) throw new Error(`Upload failed (${response.status})`);
  return response.json();
}

export async function askBusinessAdvisor(datasetId: string, question: string) {
  const response = await fetch(`${API_BASE}/api/advisor/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, question })
  });
  if (!response.ok) throw new Error(`Advisor request failed (${response.status})`);
  return response.json();
}