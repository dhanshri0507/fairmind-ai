import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { scanDataset } from "../api/client";
import toast from "react-hot-toast";
import { Upload, FileText, AlertCircle } from "lucide-react";

export default function UploadHub({ onScanComplete }) {
  const [file, setFile] = useState(null);
  const [targetCol, setTargetCol] = useState("");
  const [protectedAttrs, setProtectedAttrs] = useState("");
  const [positiveLabel, setPositiveLabel] = useState("1");
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      toast.success(`📁 ${accepted[0].name} loaded`, { className: "toast-success" });
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  const handleScan = async () => {
    if (!file) return toast.error("Please upload a CSV file first.", { className: "toast-error" });
    if (!targetCol.trim()) return toast.error("Enter the target column name.", { className: "toast-error" });
    if (!protectedAttrs.trim()) return toast.error("Enter at least one protected attribute.", { className: "toast-error" });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_column", targetCol.trim());
    formData.append("protected_attributes", protectedAttrs.trim());
    formData.append("positive_label", positiveLabel.trim());

    setLoading(true);
    try {
      const result = await scanDataset(formData);
      toast.success("✅ Audit complete!", { className: "toast-success" });
      onScanComplete(result);
    } catch (err) {
      const msg = err?.response?.data?.error || "Scan failed. Check your CSV format.";
      toast.error(msg, { className: "toast-error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-up">
      <div className="card-header">
        <span className="card-title">
          <div className="card-icon" style={{ background: "rgba(59,130,246,0.15)" }}>
            <Upload size={16} color="#3b82f6" />
          </div>
          Upload Dataset
        </span>
        <span className="badge badge-blue">CSV Only</span>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""} ${file ? "has-file" : ""}`}
        style={{ marginBottom: 24 }}
      >
        <input {...getInputProps()} />
        <div className="dropzone-icon">
          {file ? "✅" : isDragActive ? "📂" : "📊"}
        </div>
        {file ? (
          <>
            <p className="dropzone-text" style={{ color: "#10b981", fontWeight: 600 }}>
              <FileText size={14} style={{ display: "inline", marginRight: 4 }} />
              {file.name}
            </p>
            <p className="dropzone-hint">{(file.size / 1024).toFixed(1)} KB — click to replace</p>
          </>
        ) : (
          <>
            <p className="dropzone-text">Drop your CSV here or click to browse</p>
            <p className="dropzone-hint">Supports UTF-8 encoded CSV files up to 50 MB</p>
          </>
        )}
      </div>

      {/* Config fields */}
      <div className="form-grid form-grid-2" style={{ marginBottom: 16 }}>
        <div className="input-group">
          <label className="input-label">Target Column *</label>
          <input
            className="input"
            placeholder="e.g. loan_approved"
            value={targetCol}
            onChange={(e) => setTargetCol(e.target.value)}
          />
        </div>
        <div className="input-group">
          <label className="input-label">Positive Label *</label>
          <input
            className="input"
            placeholder="e.g. 1 or yes"
            value={positiveLabel}
            onChange={(e) => setPositiveLabel(e.target.value)}
          />
        </div>
      </div>

      <div className="input-group" style={{ marginBottom: 24 }}>
        <label className="input-label">Protected Attributes * (comma-separated)</label>
        <input
          className="input"
          placeholder="e.g. gender, race, age_group"
          value={protectedAttrs}
          onChange={(e) => setProtectedAttrs(e.target.value)}
        />
      </div>

      <div className="alert alert-blue" style={{ marginBottom: 20 }}>
        <span className="alert-icon"><AlertCircle size={16} /></span>
        <span>Columns must match exactly the CSV headers (case-sensitive).</span>
      </div>

      <button
        id="btn-run-scan"
        className="btn btn-primary btn-full btn-lg"
        onClick={handleScan}
        disabled={loading}
      >
        {loading ? (
          <>
            <div className="spinner" />
            Running Audit…
          </>
        ) : (
          <>
            <Upload size={18} />
            Run Bias Scan
          </>
        )}
      </button>
    </div>
  );
}
