import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { runSimulation } from "../api/client";
import toast from "react-hot-toast";
import { Wand2, ArrowRight } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const STRATEGIES = [
  { value: "reweighing",      label: "Reweighing",       desc: "Adjusts sample weights to equalise group representation" },
  { value: "threshold",       label: "Threshold Tuning",  desc: "Calibrates decision thresholds per group" },
  { value: "equalized_odds",  label: "Equalized Odds",    desc: "Constrains TPR/FPR equality across groups" },
];

export default function Simulator() {
  const [file, setFile] = useState(null);
  const [targetCol, setTargetCol] = useState("");
  const [protectedAttr, setProtectedAttr] = useState("");
  const [positiveLabel, setPositiveLabel] = useState("1");
  const [strategy, setStrategy] = useState("reweighing");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  const handleSimulate = async () => {
    if (!file) return toast.error("Upload a CSV first.", { className: "toast-error" });
    if (!targetCol || !protectedAttr) return toast.error("Fill in all fields.", { className: "toast-error" });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_column", targetCol.trim());
    formData.append("protected_attribute", protectedAttr.trim());
    formData.append("positive_label", positiveLabel.trim());
    formData.append("mitigation_strategy", strategy);

    setLoading(true);
    try {
      const data = await runSimulation(formData);
      setResult(data);
      toast.success("Simulation complete!", { className: "toast-success" });
    } catch (err) {
      toast.error(err?.response?.data?.error || "Simulation failed.", { className: "toast-error" });
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? [
        {
          name: "Demographic Parity Gap",
          Before: result.before.demographic_parity_gap,
          After: result.after.demographic_parity_gap,
        },
        {
          name: "Equalized Odds Gap",
          Before: result.before.equalized_odds_gap,
          After: result.after.equalized_odds_gap,
        },
      ]
    : [];

  const selectedStrategy = STRATEGIES.find((s) => s.value === strategy);

  return (
    <div className="card fade-up">
      <div className="card-header">
        <span className="card-title">
          <div className="card-icon" style={{ background: "rgba(16,185,129,0.15)" }}>
            <Wand2 size={16} color="#10b981" />
          </div>
          Bias Mitigation Simulator
        </span>
        <span className="badge badge-green">What-If Analysis</span>
      </div>

      {/* File drop */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""} ${file ? "has-file" : ""}`}
        style={{ padding: "24px", marginBottom: 20 }}
      >
        <input {...getInputProps()} />
        <p className="dropzone-text">
          {file ? `✅ ${file.name}` : "Drop CSV for simulation"}
        </p>
        <p className="dropzone-hint">Same dataset used for scanning works best</p>
      </div>

      <div className="form-grid form-grid-2" style={{ marginBottom: 16 }}>
        <div className="input-group">
          <label className="input-label">Target Column</label>
          <input className="input" placeholder="e.g. loan_approved" value={targetCol} onChange={(e) => setTargetCol(e.target.value)} />
        </div>
        <div className="input-group">
          <label className="input-label">Positive Label</label>
          <input className="input" placeholder="e.g. 1" value={positiveLabel} onChange={(e) => setPositiveLabel(e.target.value)} />
        </div>
      </div>

      <div className="input-group" style={{ marginBottom: 16 }}>
        <label className="input-label">Protected Attribute (single column)</label>
        <input className="input" placeholder="e.g. gender" value={protectedAttr} onChange={(e) => setProtectedAttr(e.target.value)} />
      </div>

      <div className="input-group" style={{ marginBottom: 20 }}>
        <label className="input-label">Mitigation Strategy</label>
        <select className="input" value={strategy} onChange={(e) => setStrategy(e.target.value)}>
          {STRATEGIES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        {selectedStrategy && (
          <p style={{ fontSize: "0.78rem", color: "#64748b", marginTop: 4 }}>
            {selectedStrategy.desc}
          </p>
        )}
      </div>

      <button
        id="btn-run-simulation"
        className="btn btn-primary btn-full"
        onClick={handleSimulate}
        disabled={loading}
        style={{ marginBottom: 24 }}
      >
        {loading ? <><div className="spinner" /> Simulating…</> : <><Wand2 size={16} /> Run Simulation</>}
      </button>

      {/* Results */}
      {result && (
        <div className="fade-up">
          <div className="divider" />
          <h3 style={{ fontSize: "0.9rem", fontWeight: 700, marginBottom: 16, color: "#94a3b8" }}>
            📈 Simulation Results — {STRATEGIES.find(s => s.value === result.strategy)?.label}
          </h3>

          {/* Before / After comparison */}
          <div className="compare-grid" style={{ marginBottom: 24 }}>
            <div className="compare-box before">
              <p className="compare-label">Before</p>
              <p className="compare-val">{result.before.demographic_parity_gap.toFixed(3)}</p>
              <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: 4 }}>DP Gap</p>
              <p className="compare-val" style={{ marginTop: 8 }}>{result.before.equalized_odds_gap.toFixed(3)}</p>
              <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: 4 }}>EO Gap</p>
            </div>
            <div className="compare-arrow">
              <ArrowRight size={28} color="#3b82f6" />
            </div>
            <div className="compare-box after">
              <p className="compare-label">After</p>
              <p className="compare-val">{result.after.demographic_parity_gap.toFixed(3)}</p>
              <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: 4 }}>DP Gap</p>
              <p className="compare-val" style={{ marginTop: 8 }}>{result.after.equalized_odds_gap.toFixed(3)}</p>
              <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: 4 }}>EO Gap</p>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,120,180,0.1)" />
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} domain={[0, 1]} />
                <Tooltip
                  contentStyle={{ background: "#111827", border: "1px solid #1e3a5f", borderRadius: 8, color: "#f0f4ff" }}
                  formatter={(v) => v.toFixed(3)}
                  cursor={{ fill: "rgba(255,255,255,0.05)" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Bar dataKey="Before" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="After"  fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Improvement badge */}
          {result.improvement && (
            <div className="alert alert-green" style={{ marginTop: 16 }}>
              <span className="alert-icon">🎯</span>
              <span>
                DP Gap reduced by <strong>{result.improvement.demographic_parity_gap.toFixed(3)}</strong> ·
                Fairness score delta: <strong>+{result.improvement.fairness_score_delta}</strong>
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
