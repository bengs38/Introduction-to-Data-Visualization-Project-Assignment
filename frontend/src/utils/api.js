import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 120000,
});

export function getErrorMessage(error) {
  return error?.response?.data?.detail || error?.message || "Beklenmeyen bir hata oluştu.";
}
