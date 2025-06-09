import React from 'react';

export default function Dashboard() {
  return (
    <main className="glass-card dashboard">
      <h1>Welcome to CodeQuest Arena</h1>
      <p>
        Gamified PR review, analytics, bugs, rewards, and more—all in a modern glassy dashboard.
      </p>
      {/* Feature modules go here (cards, summaries, etc) */}
      <div className="dashboard-features">
        {/* Example: Place holder cards for each feature */}
        <div className="glass-card">PR Integration</div>
        <div className="glass-card">Bug Logging & Peer Review</div>
        <div className="glass-card">Gamification</div>
        <div className="glass-card">Redeem Center</div>
        <div className="glass-card">Analytics</div>
        <div className="glass-card">Notifications</div>
        <div className="glass-card">Security & Fairness</div>
      </div>
    </main>
  );
}
