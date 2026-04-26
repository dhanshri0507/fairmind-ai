import MetricCard from "./MetricCard";
import { downloadReport } from "../api/client";
import CasualToggle from "./CasualToggle";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, Cell,
} from "recharts";
import { Download, ShieldCheck, ShieldAlert } from "lucide-react";

const BASE_URL = import.meta.env.VITE_API_URL || "https://fairmindai-production.up.railway.app";

function severityColor(s) {
  if (s === "HIGH")   return "red";
  if (s === "MEDIUM") return "yellow";
  return "green";
}

function gapColor(gap) {
  if (gap > 0.2) return "#ef4444";
  if (gap > 0.1) return "#f59e0b";
  return "#10b981";
}

export default function Dashboard({ results }) {
  if (!results) return null;

  const { audit_id, fairness_score, overall_bias_detected, dataset_size, per_attribute, filename } = results;

  const scoreColor = fairness_score >= 80 ? "green" : fairness_score >= 60 ? "yellow" : "red";

  const attrs = per_attribute ? Object.keys(per_attribute) : [];

  // Radar data — one entry per protected attribute
  const radarData = attrs.map((attr) => ({
    attribute: attr,
    "DP Gap": +(per_attribute[attr].demographic_parity_gap * 100).toFixed(1),
    "EO Gap": +(per_attribute[attr].equalized_odds_gap * 100).toFixed(1),
  }));

  // Bar chart: positive rates per group for first attribute
  const firstAttr = attrs[0];
  const groupBarData = firstAttr
    ? Object.entries(per_attribute[firstAttr].group_statistics || {}).map(([grp, stats]) => ({
        group: grp,
        "Positive Rate": +(stats.positive_rate * 100).toFixed(1),
        count: stats.count,
      }))
    : [];

  return (
    <div className="fade-up">
      {/* Summary banner */}
      <div className={`alert ${overall_bias_detected ? "alert-red" : "alert-green"}`} style={{ marginBottom: 24 }}>
        <span className="alert-icon">
          {overall_bias_detected ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
        </span>
        <div>
          <strong>{overall_bias_detected ? "⚠️ Bias Detected" : "✅ No Significant Bias"}</strong>
          <span style={{ marginLeft: 8, opacity: 0.8 }}>
            {filename} · {dataset_size?.toLocaleString()} rows · Audit ID: {audit_id?.slice(0, 8)}…
          </span>
        </div>
        <button
          onClick={async () => {
            try {
              const blobData = await downloadReport(audit_id);
              const blob = new Blob([blobData], { type: "application/pdf" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `fairmind_report_${audit_id?.slice(0, 8) || "audit"}.pdf`;
              a.click();
              setTimeout(() => URL.revokeObjectURL(url), 500);
            } catch (err) {
              console.error(err);
              alert("Could not download the PDF report.");
            }
          }}
          className="btn btn-ghost btn-sm"
          style={{ marginLeft: "auto", whiteSpace: "nowrap" }}
        >
          <Download size={14} /> Download Report
        </button>
      </div>

      {/* KPI cards */}
      <div className="metric-grid" style={{ marginBottom: 24 }}>
        <MetricCard
          label="Fairness Score"
          value={`${fairness_score}/100`}
          sub="Higher is fairer"
          color={scoreColor}
          icon="🛡️"
        />
        <MetricCard
          label="Dataset Size"
          value={dataset_size?.toLocaleString()}
          sub="Total rows analysed"
          color="blue"
          icon="📊"
        />
        <MetricCard
          label="Protected Attributes"
          value={attrs.length}
          sub="Columns evaluated"
          color="purple"
          icon="🔍"
        />
        <MetricCard
          label="Bias Status"
          value={overall_bias_detected ? "Biased" : "Fair"}
          sub={overall_bias_detected ? "Action required" : "Within thresholds"}
          color={overall_bias_detected ? "red" : "green"}
          icon={overall_bias_detected ? "⚠️" : "✅"}
        />
      </div>

      {/* Charts */}
      {attrs.length > 0 && (
        <div className="page-grid" style={{ marginBottom: 24 }}>
          {/* Radar: DP and EO gaps */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">📡 Bias Gaps by Attribute (%)</span>
            </div>
            <div className="chart-area">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(99,120,180,0.15)" />
                  <PolarAngleAxis dataKey="attribute" tick={{ fill: "#64748b", fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 30]} tick={{ fill: "#475569", fontSize: 10 }} />
                  <Radar name="DP Gap" dataKey="DP Gap" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.25} />
                  <Radar name="EO Gap" dataKey="EO Gap" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} />
                  <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e3a5f", borderRadius: 8, color: "#f0f4ff" }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bar: positive rates per group (first attribute) */}
          {firstAttr && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">📊 Positive Rates — {firstAttr}</span>
              </div>
              <div className="chart-area">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={groupBarData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,120,180,0.1)" />
                    <XAxis dataKey="group" tick={{ fill: "#64748b", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#64748b", fontSize: 11 }} unit="%" domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{ background: "#111827", border: "1px solid #1e3a5f", borderRadius: 8, color: "#f0f4ff" }}
                      formatter={(v) => `${v}%`}
                      cursor={{ fill: "rgba(255,255,255,0.05)" }}
                    />
                    <Bar dataKey="Positive Rate" radius={[6, 6, 0, 0]}>
                      {groupBarData.map((_, i) => (
                        <Cell key={i} fill={["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"][i % 5]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Per-attribute detail cards */}
      {attrs.map((attr) => {
        const a = per_attribute[attr];
        const color = severityColor(a.severity);
        return (
          <div key={attr} className="card" style={{ marginBottom: 16 }}>
            <div className="card-header">
              <span className="card-title">
                🏷️ {attr}
              </span>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span className={`badge badge-${color}`}>
                  {a.severity} RISK
                </span>
                <span className={`badge ${a.bias_detected ? "badge-red" : "badge-green"}`}>
                  {a.bias_detected ? "Bias Detected" : "Fair"}
                </span>
              </div>
            </div>

            <div className="form-grid form-grid-2" style={{ marginBottom: 16 }}>
              <div>
                <p style={{ fontSize: "0.72rem", color: "#475569", textTransform: "uppercase", marginBottom: 4 }}>Demographic Parity Gap</p>
                <p style={{ fontSize: "1.5rem", fontWeight: 700, color: gapColor(a.demographic_parity_gap) }}>
                  {a.demographic_parity_gap.toFixed(3)}
                </p>
                <div className="progress-wrap" style={{ marginTop: 6 }}>
                  <div
                    className="progress-bar"
                    style={{ width: `${Math.min(a.demographic_parity_gap * 200, 100)}%`, background: gapColor(a.demographic_parity_gap) }}
                  />
                </div>
              </div>
              <div>
                <p style={{ fontSize: "0.72rem", color: "#475569", textTransform: "uppercase", marginBottom: 4 }}>Equalized Odds Gap</p>
                <p style={{ fontSize: "1.5rem", fontWeight: 700, color: gapColor(a.equalized_odds_gap) }}>
                  {a.equalized_odds_gap.toFixed(3)}
                </p>
                <div className="progress-wrap" style={{ marginTop: 6 }}>
                  <div
                    className="progress-bar"
                    style={{ width: `${Math.min(a.equalized_odds_gap * 200, 100)}%`, background: gapColor(a.equalized_odds_gap) }}
                  />
                </div>
              </div>
            </div>

            {/* Group statistics table */}
            {a.group_statistics && (
              <table className="group-table">
                <thead>
                  <tr>
                    <th>Group</th>
                    <th>Count</th>
                    <th>Positive Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(a.group_statistics).map(([grp, stats]) => (
                    <tr key={grp}>
                      <td style={{ fontWeight: 500, color: "#e2e8f0" }}>{grp}</td>
                      <td>{stats.count.toLocaleString()}</td>
                      <td>
                        <span style={{ color: gapColor(0.5 - stats.positive_rate), fontWeight: 600 }}>
                          {(stats.positive_rate * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        );
      })}

      {/* Gemini explanation toggle */}
      {audit_id && <CasualToggle auditId={audit_id} results={results} />}
    </div>
  );
}
