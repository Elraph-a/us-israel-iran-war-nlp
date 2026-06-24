import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const getOverview = () => api.get("/api/overview").then((r) => r.data);
export const getTopics = () => api.get("/api/topics").then((r) => r.data);
export const getSentiment = () => api.get("/api/sentiment").then((r) => r.data);
export const analyzeText = (text) =>
  api.post("/api/analyze", { text }).then((r) => r.data);

export default api;
