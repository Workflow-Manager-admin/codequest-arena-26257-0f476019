import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';
// Feature page stubs
import PRDashboard from './pages/PRDashboard';
import BugPanel from './pages/BugPanel';
import Rules from './pages/Rules';
import Analytics from './pages/Analytics';
import Gamification from './pages/Gamification';
import RedeemCenter from './pages/RedeemCenter';
import Login from './pages/Login';
import { useAuth } from './hooks/useAuth';

function AuthWrapper({ children }) {
  // Very simple route auth guard for the demo
  const auth = useAuth();
  if (!auth.isAuthenticated) {
    window.location.href = "/login";
    return null;
  }
  return children;
}

export default function App() {
  const auth = useAuth();

  return (
    <Router>
      <div className="glass-app-shell">
        {/* Glassy navigation bar */}
        <nav style={{
            display: 'flex',
            gap: '1.5rem',
            padding: '1.5rem',
            justifyContent: 'center',
            alignItems: 'center',
            background: 'rgba(2,13,29,0.65)',
            borderBottom: '1.5px solid rgba(255,255,255,0.11)',
            boxShadow: '0 2px 16px 0 rgba(2,13,29,0.06)',
            zIndex: 10,
          }}>
          <Link to="/" style={{ color: '#00eaff', fontWeight: 600, fontSize: 20 }}>
            CodeQuest Arena
          </Link>
          <Link to="/prs">PRs</Link>
          <Link to="/bugs">Bugs</Link>
          <Link to="/rules">Rules</Link>
          <Link to="/analytics">Analytics</Link>
          <Link to="/gamification">Gamification</Link>
          <Link to="/redeem">Redeem Center</Link>
          {/* Spacer */}
          <span style={{ flex: 1 }} />
          {auth.isAuthenticated ? (
            <>
              <span style={{ color: "#26ffb8", fontWeight: 500 }}>{auth.username}</span>
              <button
                onClick={auth.logout}
                style={{
                  background: "#181d24",
                  color: "#ff4545",
                  border: 0,
                  fontWeight: 600,
                  cursor: "pointer",
                  padding: "4px 16px",
                  borderRadius: 8,
                  marginLeft: 10,
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              style={{
                background: "#00eaff",
                color: "#181d24",
                padding: "4px 18px",
                borderRadius: 8,
                fontWeight: 600,
                marginLeft: 8,
              }}
            >
              Login
            </Link>
          )}
        </nav>
        <Routes>
          <Route path="/" element={<AuthWrapper><Dashboard /></AuthWrapper>} />
          <Route path="/prs" element={<AuthWrapper><PRDashboard /></AuthWrapper>} />
          <Route path="/bugs" element={<AuthWrapper><BugPanel /></AuthWrapper>} />
          <Route path="/rules" element={<AuthWrapper><Rules /></AuthWrapper>} />
          <Route path="/analytics" element={<AuthWrapper><Analytics /></AuthWrapper>} />
          <Route path="/gamification" element={<AuthWrapper><Gamification /></AuthWrapper>} />
          <Route path="/redeem" element={<AuthWrapper><RedeemCenter /></AuthWrapper>} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Router>
  );
}
