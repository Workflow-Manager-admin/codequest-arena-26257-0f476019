import React from "react";

/**
 * PR Dashboard Page (stub).
 * Displays pull requests and repo management (to be implemented).
 */
export default function PRDashboard() {
  return (
    <div className="glass-card">
      <h1>PR Dashboard</h1>
      <p>
        This is the PR integration & repository management page.<br />
        Here you will be able to view repositories, connect to GitHub/GitLab/Bitbucket, and manage pull requests.
      </p>
      <div className="glass-card" style={{ marginTop: 20 }}>
        <b>[Stub]</b> PR list, repo navigation, OAuth integration UI will appear here.
      </div>
    </div>
  );
}
