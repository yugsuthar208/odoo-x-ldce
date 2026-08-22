export function SkeletonCard({ className = "" }) {
  return (
    <div className={`card ${className}`} style={{ padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
      <div className="skeleton" style={{ height: 14, width: "60%", borderRadius: 8 }} />
      <div className="skeleton" style={{ height: 12, width: "40%", borderRadius: 8 }} />
      <div className="skeleton" style={{ height: 4, width: "100%", borderRadius: 999, marginTop: 4 }} />
      <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
        <div className="skeleton" style={{ height: 22, width: 70, borderRadius: 999 }} />
        <div className="skeleton" style={{ height: 22, width: 90, borderRadius: 999 }} />
      </div>
    </div>
  );
}

export function SkeletonText({ width = "100%", height = 14, style = {} }) {
  return (
    <div
      className="skeleton"
      style={{ height, width, borderRadius: 8, ...style }}
    />
  );
}
