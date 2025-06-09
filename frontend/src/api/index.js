// API client setup for CodeQuest Arena backend.
// Example: import axios from 'axios'; export configured instance.

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export default api;

// Add feature API functions in per-feature modules (e.g. api/pr.js, api/bug.js, ...)
