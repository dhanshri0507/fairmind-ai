export default function MetricCard({ label, value, sub, color = "blue", icon }) {
  return (
    <div className={`metric-card ${color}`}>
      <p className="metric-card-label">{label}</p>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {icon && <span style={{ fontSize: "1.4rem" }}>{icon}</span>}
        <p className={`metric-card-value ${color}`}>{value}</p>
      </div>
      {sub && <p className="metric-card-sub">{sub}</p>}
    </div>
  );
}
