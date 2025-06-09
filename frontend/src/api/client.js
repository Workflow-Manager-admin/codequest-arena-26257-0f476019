import axios from "axios";

/**
 * Core API client for CodeQuest Arena.
 * Configures baseURL from environment, sets up GET/POST helpers,
 * and centralized error handling.
 */

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000", // fallback dev URL
  timeout: 12000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// PUBLIC_INTERFACE
export async function apiGet(url, config = {}) {
  /** GET request helper with error handling */
  try {
    const response = await api.get(url, config);
    return response.data;
  } catch (err) {
    handleApiError(err);
  }
}

// PUBLIC_INTERFACE
export async function apiPost(url, data = {}, config = {}) {
  /** POST request helper with error handling */
  try {
    const response = await api.post(url, data, config);
    return response.data;
  } catch (err) {
    handleApiError(err);
  }
}

// Scaffold for unified API error handling
function handleApiError(error) {
  if (error.response) {
    // Server responded with a code outside 2xx
    /* Could add toast/UI notification here */
    throw new Error(
      error.response.data?.detail ||
        `API Error: ${error.response.status} (${error.response.statusText})`
    );
  } else if (error.request) {
    // No response received
    throw new Error("No response from server. Is the backend running?");
  } else {
    // Setup/other error
    throw new Error(error.message || "API client error");
  }
}

// Example: features API (list features/rules etc)
export async function fetchFeatures() {
  // GET /features
  return apiGet("/features");
}

export async function fetchRules() {
  // GET /rules
  return apiGet("/rules");
}

// Extend: add other API modules or helpers as needed (analytics, PRs, etc)
