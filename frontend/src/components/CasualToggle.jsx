import { useState } from "react";
import { getExplanation } from "../api/client";
import toast from "react-hot-toast";
import { Brain, Zap } from "lucide-react";

export default function CasualToggle({ auditId, results }) {
  const [mode, setMode] = useState("professional");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [cache, setCache] = useState({});

  const switchMode = async (newMode) => {
    setMode(newMode);

    // Use cached response — avoid duplicate API calls
    if (cache[newMode]) {
      setExplanation(cache[newMode]);
      return;
    }

    setLoading(true);
    try {
      const data = await getExplanation(auditId, newMode, results);
      if (data?.error) throw new Error(data.error);
      setExplanation(data.explanation || "");
      setCache((prev) => ({ ...prev, [newMode]: data.explanation }));
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        "Could not load explanation right now.";
      setExplanation(msg);
      toast.error(err?.response?.data?.error || "Gemini explanation failed.", { className: "toast-error" });
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
          <span style={{ fontSize: "0.72rem", color: "#64748b", fontWeight: 400 }}>
            Powered by Gemini 2.5 Flash
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
        <div className={`explanation-box ${mode}`}>
          {explanation}
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
