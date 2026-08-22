import { GripVertical, Clock, DollarSign, X } from "lucide-react";

export function ActivityList({ items = [], onRemove }) {
  if (items.length === 0) {
    return <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem", fontStyle: "italic", padding: "16px 0" }}>No activities planned yet.</p>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {items.map((item, idx) => {
        const act = item.activity;
        return (
          <div key={item.id} className="card" style={{ padding: 12, display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ color: "var(--border)", cursor: "grab" }}>
              <GripVertical size={16} />
            </div>
            
            <div style={{ width: 48, height: 48, borderRadius: 8, background: "var(--surface)", overflow: "hidden", flexShrink: 0 }}>
              {act?.image_url && <img src={act.image_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                <h4 style={{ margin: 0, fontSize: "0.9375rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{act?.name}</h4>
                <span className={`pill pill--${act?.category?.toLowerCase()}`} style={{ fontSize: "0.65rem", padding: "2px 6px" }}>{act?.category}</span>
              </div>
              <div style={{ display: "flex", gap: 12, color: "var(--ink-soft)", fontSize: "0.75rem" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 3 }}><Clock size={12} /> {act?.duration_hours}h</span>
                <span style={{ display: "flex", alignItems: "center", gap: 3, fontWeight: 600, color: "var(--accent)" }}>₹{Number(item.custom_cost ?? act?.estimated_cost ?? 0).toLocaleString('en-IN')}</span>
              </div>
            </div>

            <button className="btn btn--icon btn--ghost" onClick={() => onRemove(item.id)} style={{ color: "var(--danger)" }}>
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
