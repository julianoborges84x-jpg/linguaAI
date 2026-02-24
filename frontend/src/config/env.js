// frontend/src/config/env.js
export const ENV = {
  API_URL: (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, ""),
};