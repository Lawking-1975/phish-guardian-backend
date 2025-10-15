// src/api.js
import axios from "axios";

// Use Vite environment variable for API base URL if set, fallback to local dev
const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

/**
 * Send a URL to the backend for phishing prediction.
 * @param {string} url - The URL to check
 * @returns {Promise<Object>} - Prediction result from backend
 */
export async function predictUrl(url) {
  try {
    const response = await axios.post(`${API_BASE}/predict`, { url });
    return response.data;
  } catch (err) {
    console.error("Error calling backend /predict:", err);
    // Return a standard error object for frontend handling
    return {
      url,
      status: "error",
      message: "Could not reach backend. Ensure backend is running and CORS allows this origin.",
    };
  }
}
