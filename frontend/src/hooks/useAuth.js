import { useState, useEffect } from "react";

// Load token from localStorage (if any)
function getInitialAuth() {
  const token = localStorage.getItem("cq_token");
  const username = localStorage.getItem("cq_user");
  return {
    isAuthenticated: !!token,
    token: token || null,
    username: username || null,
  };
}

// PUBLIC_INTERFACE
export function useAuth() {
  const [auth, setAuth] = useState(getInitialAuth());

  const login = (token, username) => {
    localStorage.setItem("cq_token", token);
    localStorage.setItem("cq_user", username);
    setAuth({ isAuthenticated: true, token, username });
  };

  const logout = () => {
    localStorage.removeItem("cq_token");
    localStorage.removeItem("cq_user");
    setAuth({ isAuthenticated: false, token: null, username: null });
  };

  useEffect(() => {
    setAuth(getInitialAuth());
  }, []);

  return { ...auth, login, logout };
}
