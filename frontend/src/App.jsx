import { useState } from "react";
import { Toaster } from "react-hot-toast";
import UploadHub from "./components/UploadHub";
import Dashboard from "./components/Dashboard";
import Simulator from "./components/Simulator";
import "./index.css";

const NAV = ["Scan", "Simulate", "About"];

export default function App() {
  const [activeTab, setActiveTab] = useState("Scan");
  const [scanResults, setScanResults] = useState(null);

  const handleScanComplete = (results) => {
    setScanResults(results);
  };

  return (
    <div className="app-wrapper">
      <Toaster position="top-right" />

      {/* ── Header ── */}
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <div className="logo">
              <div className="logo-icon">⚖️</div>
              <span className="logo-text">FairMind AI</span>
              <span className="logo-badge">BETA</span>
            </div>
            <nav className="header-nav">
              {NAV.map((tab) => (
                <button
                  key={tab}
                  id={`nav-${tab.toLowerCase()}`}
                  className={`nav-btn ${activeTab === tab ? "active" : ""}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="container">
        {/* ── Hero ── */}
        {activeTab === "Scan" && (
          <section className="hero">
            <div className="hero-tag">
              <span>🤖</span>
              Hack2Skill Build with AI 2026 · Solution Challenge
            </div>
            <h1 className="hero-title">
              Detect &amp; Mitigate<br />
              <span className="highlight">AI Bias Instantly</span>
            </h1>
            <p className="hero-subtitle">
              Upload your dataset. FairMind analyses fairness metrics across protected groups
              and explains the results in plain language — powered by Gemini-2.5-flash.
            </p>
            <div className="hero-stats">
              <div className="hero-stat">
                <span className="hero-stat-value">fairlearn</span>
                <span className="hero-stat-label">Fairness Engine</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-value">Gemini 2.5</span>
                <span className="hero-stat-label">AI Explainer</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-value">Supabase</span>
                <span className="hero-stat-label">Audit Logs</span>
              </div>
            </div>
          </section>
        )}

        {/* ── Scan Tab ── */}
        {activeTab === "Scan" && (
          <div className="section">
            <div className="page-grid">
              <UploadHub onScanComplete={handleScanComplete} />
              {!scanResults && (
                <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
                  <div className="empty-state">
                    <div className="empty-icon">⚖️</div>
                    <p className="empty-text">Your audit results will appear here</p>
                    <p className="empty-hint">Upload a CSV and run a bias scan to get started</p>
                  </div>
                </div>
              )}
            </div>
            {scanResults && (
              <div style={{ marginTop: 32 }}>
                <div className="section-title">Audit Results</div>
                <p className="section-sub">
                  Bias analysis across {Object.keys(scanResults.per_attribute || {}).length} protected attributes
                </p>
                <Dashboard results={scanResults} />
              </div>
            )}
          </div>
        )}

        {/* ── Simulate Tab ── */}
        {activeTab === "Simulate" && (
          <div className="section">
            <div className="section-title">⚗️ Bias Mitigation Simulator</div>
            <p className="section-sub">
              Test mitigation strategies and see the predicted fairness improvement before applying them.
            </p>
            <div style={{ maxWidth: 700 }}>
              <Simulator />
            </div>
          </div>
        )}

        {/* ── About Tab ── */}
        {activeTab === "About" && (
          <div className="section" style={{ maxWidth: 760 }}>
            <div className="hero-tag" style={{ marginBottom: 20 }}>⚖️ About FairMind AI</div>
            <h2 className="section-title">Built for Responsible AI</h2>
            <p className="section-sub" style={{ marginBottom: 32 }}>
              FairMind AI is an open-source bias detection and mitigation platform designed for the
              Google Build with AI · Solution Challenge 2026.
            </p>

            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title" style={{ marginBottom: 12 }}>🛠️ Technology Stack</div>
              <div className="form-grid form-grid-2">
                {[
                  ["Backend", "FastAPI · Python 3.11"],
                  ["Fairness Engine", "fairlearn · aif360"],
                  ["AI Explainer", "Google Gemini 2.5 Flash"],
                  ["Database", "Supabase (PostgreSQL)"],
                  ["Frontend", "React 18 · Recharts"],
                  ["Deployment", "Railway · Vercel"],
                ].map(([k, v]) => (
                  <div key={k} style={{ padding: "12px 0", borderBottom: "1px solid rgba(99,120,180,0.1)" }}>
                    <p style={{ fontSize: "0.72rem", color: "#475569", textTransform: "uppercase", marginBottom: 4 }}>{k}</p>
                    <p style={{ fontSize: "0.9rem", fontWeight: 500, color: "#cbd5e1" }}>{v}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-title" style={{ marginBottom: 12 }}>📐 Fairness Metrics Explained</div>
              {[
                ["Demographic Parity Gap", "Difference in positive prediction rates between groups. A gap > 0.1 indicates bias."],
                ["Equalized Odds Gap", "Difference in true positive rates across groups. Ensures equal opportunity."],
                ["Fairness Score", "Composite 0–100 score. 80+ is considered fair by international guidelines."],
              ].map(([term, def]) => (
                <div key={term} style={{ marginBottom: 16 }}>
                  <p style={{ fontWeight: 600, fontSize: "0.875rem", color: "#93c5fd", marginBottom: 4 }}>{term}</p>
                  <p style={{ fontSize: "0.85rem", color: "#64748b", lineHeight: 1.6 }}>{def}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ textAlign: "center", padding: "40px 0 24px", color: "#334155", fontSize: "0.8rem" }}>
        FairMind AI · Build with AI Solution Challenge 2026 · Powered by Google Gemini
      </footer>
    </div>
  );
}
