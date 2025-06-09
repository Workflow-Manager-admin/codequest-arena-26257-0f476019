import React, { useEffect, useState } from 'react';
import { fetchFeatures, fetchRules } from '../api/client';

/**
 * Dashboard: Fetches feature + rules list from backend API.
 * Demonstrates real API wiring/scaffolding, loading states, and error handling.
 */
export default function Dashboard() {
  const [featureList, setFeatureList] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errMsg, setErrMsg] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [featuresResp, rulesResp] = await Promise.all([
          fetchFeatures(),
          fetchRules(),
        ]);
        setFeatureList(featuresResp.features ?? []);
        setRules(rulesResp ?? []);
        setErrMsg('');
      } catch (err) {
        setErrMsg(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <main className="glass-card dashboard">
      <h1>Welcome to CodeQuest Arena</h1>
      <p>
        Gamified PR review, analytics, bugs, rewards, and more—<b>powered by a modern API + glassy dashboard</b>.
      </p>
      {loading && <div className="glass-card">Loading live data…</div>}
      {errMsg && <div className="glass-card" style={{ color: '#ff4545' }}>{errMsg}</div>}
      {!loading && !errMsg && (
        <>
          {/* Dynamic features from API */}
          <div className="dashboard-features">
            {featureList.length > 0 ? (
              featureList.map((feat, idx) => (
                <div
                  key={feat.name || idx}
                  className={`glass-card ${feat.enabled ? '' : 'glass-disabled'}`}
                >
                  <b>{feat.name}</b>
                  <br />
                  <small style={{ color: feat.enabled ? '#26ffb8' : '#aaa' }}>
                    {feat.enabled ? 'Enabled' : 'Disabled'}
                  </small>
                </div>
              ))
            ) : (
              <div className="glass-card">No features found.</div>
            )}
          </div>
          {/* Example: Rules fetched from backend */}
          <section style={{ marginTop: '2rem' }}>
            <h2>Active Rules</h2>
            <ul>
              {rules.length > 0 ? (
                rules.map((rule) => (
                  <li key={rule.id}>
                    <b>{rule.name}</b>
                    <span style={{ marginLeft: 8, color: '#00eaff' }}>
                      [{rule.severity}] ({rule.type})
                    </span>
                  </li>
                ))
              ) : (
                <li>No rules defined in backend.</li>
              )}
            </ul>
          </section>
        </>
      )}
    </main>
  );
}
