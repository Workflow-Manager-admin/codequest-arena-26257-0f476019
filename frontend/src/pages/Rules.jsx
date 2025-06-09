import React from "react";

/**
 * Rules Page (stub).
 * Displays code quality/static analysis/process policy rules.
 */
export default function Rules() {
  return (
    <div className="glass-card">
      <h1>Rule Engine</h1>
      <p>
        View and manage code quality, static analysis, and process policy rules.<br />
        Admins can define and enable/disable rules here.
      </p>
      <div className="glass-card" style={{ marginTop: 20 }}>
        <b>[Stub]</b> Rules table, add/update/delete UI will be here.
      </div>
    </div>
  );
}
