import { CalendarDays, MoreVertical } from "lucide-react";

export function StopCard({ stop, onClick, isSelected }) {
  const days = Math.round(
    (new Date(stop.departure_date) - new Date(stop.arrival_date)) / 86400000
  );

  return (
    <div
      className={`card card--hover ${isSelected ? "selected" : ""}`}
      style={{
        padding: 16,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        border: isSelected ? "2px solid var(--ink)" : "1px solid var(--border)",
        background: isSelected ? "#f9f9f9" : "var(--white)",
      }}
      onClick={onClick}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{
          width: 48, height: 48, borderRadius: "var(--radius-input)",
          background: "var(--surface)", display: "flex", alignItems: "center",
          justifyContent: "center", overflow: "hidden", flexShrink: 0
        }}>
          {stop.city?.image_url ? (
            <img src={stop.city.image_url} alt={stop.city.name} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <span style={{ fontWeight: 700, color: "var(--ink-soft)" }}>{(stop.stop_order ?? 0) + 1}</span>
          )}
        </div>
        
        <div>
          <h4 style={{ fontSize: "0.9375rem", marginBottom: 2 }}>{stop.city?.name || stop.city_name || "Destination"}</h4>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--ink-soft)", fontSize: "0.8125rem" }}>
            <CalendarDays size={12} />
            <span>{days} {days === 1 ? "day" : "days"}</span>
          </div>
        </div>
      </div>

      <button className="btn btn--icon btn--ghost" onClick={(e) => { e.stopPropagation(); /* TODO dropdown menu */ }}>
        <MoreVertical size={16} />
      </button>
    </div>
  );
}
