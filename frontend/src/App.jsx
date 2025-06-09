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

export default function App() {
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
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/prs" element={<PRDashboard />} />
          <Route path="/bugs" element={<BugPanel />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/gamification" element={<Gamification />} />
          <Route path="/redeem" element={<RedeemCenter />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Router>
  );
}
