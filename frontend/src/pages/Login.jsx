import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiLogin, apiRegister } from "../api/auth";
import { useAuth } from "../hooks/useAuth";

/**
 * Login Page - handles login and demo registration, sets auth state, handles errors.
 */
export default function Login() {
  const [tab, setTab] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errMsg, setErrMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const auth = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setErrMsg("");
    try {
      if (tab === "login") {
        const data = await apiLogin(username, password);
        auth.login(data.access_token, username);
        navigate("/");
      } else {
        await apiRegister(username, password);
        setTab("login");
        setErrMsg("Registered! Please log in.");
      }
    } catch (err) {
      setErrMsg(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card" style={{ maxWidth: 420, margin: "2rem auto" }}>
      <div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
        <button
          onClick={() => setTab("login")}
          style={{
            flex: 1,
            background: tab === "login" ? "#00eaff" : "#222c",
            color: tab === "login" ? "#101d26" : "#ccc",
            padding: 8,
            border: 0,
            borderRadius: 10,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Login
        </button>
        <button
          onClick={() => setTab("register")}
          style={{
            flex: 1,
            background: tab === "register" ? "#00eaff" : "#222c",
            color: tab === "register" ? "#101d26" : "#ccc",
            padding: 8,
            border: 0,
            borderRadius: 10,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Register
        </button>
      </div>
      <form onSubmit={handleSubmit}>
        <label>
          Username (demo: <b>demo</b>)
          <input
            type="text"
            autoFocus
            required
            value={username}
            onChange={e => setUsername(e.target.value)}
            style={{
              width: "100%",
              fontSize: 16,
              padding: 8,
              margin: "4px 0 16px 0",
              borderRadius: 8,
              border: "1.5px solid #013951",
              background: "rgba(2,13,29,0.13)",
              color: "#1deaff",
            }}
          />
        </label>
        <label>
          Password (demo: <b>demo123</b>)
          <input
            type="password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{
              width: "100%",
              fontSize: 16,
              padding: 8,
              margin: "4px 0 20px 0",
              borderRadius: 8,
              border: "1.5px solid #013951",
              background: "rgba(2,13,29,0.13)",
              color: "#1deaff",
            }}
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            background: "#00eaff",
            color: "#181d24",
            fontWeight: 600,
            fontSize: 18,
            padding: 10,
            border: 0,
            borderRadius: 10,
            marginBottom: 10,
            cursor: "pointer",
          }}
        >
          {loading
            ? tab === "login"
              ? "Logging in…"
              : "Registering…"
            : tab === "login"
            ? "Login"
            : "Register"}
        </button>
        {errMsg && (
          <div style={{ color: "#ff4545", marginTop: 6, minHeight: 18 }}>{errMsg}</div>
        )}
        {tab === "login" && (
          <div style={{ marginTop: 24, color: "#aca", fontSize: 13 }}>
            Demo user:&nbsp;<b>demo / demo123</b>
          </div>
        )}
      </form>
    </div>
  );
}
