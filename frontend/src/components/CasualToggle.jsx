import { useState } from "react";
import { getExplanation } from "../api/client";
import toast from "react-hot-toast";
import { Brain, Zap } from "lucide-react";

export default function CasualToggle({ auditId, results }) {
  const [mode, setMode] = useState("professional");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [cache, setCache] = useState({});
  const [isFallback, setIsFallback] = useState(false);

  const switchMode = async (newMode) => {
    setMode(newMode);

    // Use cached response — avoid duplicate API calls
    if (cache[newMode]) {
      setExplanation(cache[newMode]);
      return;
    }

    setLoading(true);
    setIsFallback(false);
    try {
      const data = await getExplanation(auditId, newMode, results);
      if (data?.error) throw new Error(data.error);
      const text = data.explanation || "";
      // Detect static fallback content (quota exhausted)
      const isStaticFallback = text.includes("quota reached") || text.includes("pre-generated") || text.includes("pre-written");
      setIsFallback(isStaticFallback);
      setExplanation(text);
      setCache((prev) => ({ ...prev, [newMode]: text }));
    } catch (err) {
      setIsFallback(true);
      setExplanation(
        mode === "casual"
          ? "🔍 Your AI model is treating different groups unequally — like a job process that keeps rejecting candidates from certain backgrounds.\n\nThis is fixable! Use the Simulate tab to try mitigation strategies like Reweighing.\n\n_(Gemini AI quota reached for today. Try again tomorrow!)_"
          : "## Bias Audit Summary\n\nSignificant bias was detected across protected attributes. Immediate review of training data and decision thresholds is recommended.\n\nUse the Simulate tab to apply Reweighing or Equalized Odds post-processing.\n\n_(Gemini AI quota reached. This is a pre-generated summary. Try again tomorrow!)_"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-up" style={{ marginTop: 24 }}>
      {/* Header */}
      <div className="card-header">
        <span className="card-title">
          <div className="card-icon" style={{ background: "rgba(139,92,246,0.15)" }}>
            <Brain size={16} color="#8b5cf6" />
          </div>
          Gemini Bias Explainer
          <span style={{ fontSize: "0.72rem", color: isFallback ? "#f59e0b" : "#64748b", fontWeight: 400 }}>
            {isFallback ? "⚠️ Quota reached — showing fallback" : "Powered by Gemini 2.5 Flash"}
          </span>
        </span>

        {/* Mode Toggle */}
        <div className="tabs" style={{ width: "auto" }}>
          {["professional", "casual"].map((m) => (
            <button
              key={m}
              id={`toggle-${m}`}
              className={`tab ${mode === m ? "active" : ""}`}
              onClick={() => switchMode(m)}
            >
              {m === "professional" ? "📊 Technical" : "💬 Plain English"}
            </button>
          ))}
        </div>
      </div>

      {/* Mode Badge */}
      <div
        className={`badge ${mode === "professional" ? "badge-blue" : "badge-green"}`}
        style={{ marginBottom: 16 }}
      >
        <Zap size={10} />
        {mode === "professional" ? "Audit Report Language" : "Plain English Mode"}
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "32px 0", justifyContent: "center" }}>
          <div className="spinner" />
          <span style={{ color: "#64748b", fontSize: "0.9rem" }}>Gemini is analysing your audit…</span>
        </div>
      ) : explanation ? (
        <div>
          {isFallback && (
            <div style={{
              background: "rgba(245,158,11,0.1)",
              border: "1px solid rgba(245,158,11,0.35)",
              borderRadius: 8,
              padding: "10px 14px",
              marginBottom: 12,
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: "0.82rem",
              color: "#fbbf24",
            }}>
              ⚠️ <strong>Gemini API quota reached</strong> — showing a pre-generated summary. Free tier resets daily.
            </div>
          )}
          <div className={`explanation-box ${mode}`}>
            {explanation}
          </div>
        </div>
      ) : (
        <button
          id="btn-generate-explanation"
          className="btn btn-ghost btn-full"
          onClick={() => switchMode(mode)}
          style={{ borderStyle: "dashed", borderColor: "rgba(99,120,180,0.4)" }}
        >
          ✨ Click to generate Gemini explanation
        </button>
      )}

      {/* Footer tip */}
      {explanation && !loading && (
        <p style={{ fontSize: "0.75rem", color: "#475569", marginTop: 12, textAlign: "right" }}>
          {mode === "casual"
            ? "Switch to Technical for the full audit report language"
            : "Switch to Plain English to share with non-technical stakeholders"}
        </p>
      )}
    </div>
  );
}
