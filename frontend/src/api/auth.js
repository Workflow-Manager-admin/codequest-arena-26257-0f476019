import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiLogin(username, password) {
  // POST form data as application/x-www-form-urlencoded!
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
  try {
    const resp = await axios.post(`${API_URL}/auth/login`, params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return resp.data;
  } catch (err) {
    throw new Error(
      err.response?.data?.detail ||
        err.message ||
        "Error logging in."
    );
  }
}

export async function apiRegister(username, password) {
  try {
    const resp = await axios.post(`${API_URL}/auth/register`, {
      username,
      password,
    });
    return resp.data;
  } catch (err) {
    throw new Error(
      err.response?.data?.detail ||
        err.message ||
        "Error registering."
    );
  }
}

export async function apiMe(token) {
  try {
    const resp = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  } catch (err) {
    throw new Error(
      err.response?.data?.detail ||
        err.message ||
        "Error fetching user info."
    );
  }
}
