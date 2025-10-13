// src/api.js
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";



export async function predictUrl(url) {
  const res = await axios.post(`${API_BASE}/predict`, { url });
  return res.data;
}
