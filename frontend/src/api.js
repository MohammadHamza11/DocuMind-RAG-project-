import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE,
});

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function queryDocuments(question, chatHistory) {
  const response = await api.post("/query", {
    question,
    chat_history: chatHistory,
  });
  return response.data;
}

export async function listDocuments() {
  const response = await api.get("/documents");
  return response.data;
}

export async function deleteAllDocuments() {
  const response = await api.delete("/documents");
  return response.data;
}

export default api;
