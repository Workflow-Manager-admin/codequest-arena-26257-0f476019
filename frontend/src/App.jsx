import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Example page imports (stub): Real feature pages will go here.
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <Router>
      <div className="glass-app-shell">
        {/* TODO: Navigation/sidebar, animated neon header, etc */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          {/* Add more feature routes as needed */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Router>
  );
}
