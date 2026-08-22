import { Link } from "react-router-dom";
import { Calendar, ArrowRight } from "lucide-react";

function statusPill(status) {
  const map = {
    draft:     "pill--draft",
    upcoming:  "pill--upcoming",
    ongoing:   "pill--ongoing",
    completed: "pill--completed",
  };
  return map[status] || "pill--draft";
}

function tripProgress(trip) {
  if (trip.status !== "ongoing") return null;
  const start = new Date(trip.start_date).getTime();
  const end   = new Date(trip.end_date).getTime();
  const now   = Date.now();
  const pct   = Math.min(100, Math.max(0, Math.round((now - start) / (end - start) * 100)));
  return pct;
}

export function TripCard({ trip }) {
  const pct = tripProgress(trip);
  const firstStop = trip.stops?.[0]?.city?.name;
  const lastStop  = trip.stops?.[trip.stops.length - 1]?.city?.name;
  const route     = firstStop && lastStop && firstStop !== lastStop
    ? `${firstStop} → ${lastStop}`
    : trip.title;

  const totalDays = Math.round(
    (new Date(trip.end_date) - new Date(trip.start_date)) / 86400000
  );

  const thumbUrl = trip.stops?.[0]?.city?.image_url;

  return (
    <Link to={`/trips/${trip.id}`} style={{ display: "block" }} className="stagger-item">
      <div className="card card--hover" style={{ display: "flex", overflow: "hidden", cursor: "pointer", height: "100%" }}>
        {/* Left-aligned Thumbnail */}
        <div style={{ width: 120, flexShrink: 0, background: "var(--border)" }}>
          {thumbUrl && (
            <img src={thumbUrl} alt="Destination" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          )}
        </div>
        
        {/* Card Content */}
        <div style={{ padding: 24, flex: 1, minWidth: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          {/* Top row */}
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, marginBottom: 8 }}>
            <div style={{ minWidth: 0 }}>
              <p style={{ fontWeight: 700, fontSize: "1.1rem", color: "var(--ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {route}
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 4, color: "var(--ink-soft)", fontSize: "0.8125rem", flexWrap: "wrap" }}>
                <Calendar size={12} />
                <span>{trip.start_date} — {trip.end_date}</span>
                <span style={{ opacity: 0.5 }}>·</span>
                <span>{totalDays}d</span>
                {trip.origin_city && (
                  <>
                    <span style={{ opacity: 0.5 }}>·</span>
                    <span style={{ color: "var(--accent)", fontWeight: 500 }}>From: {trip.origin_city}</span>
                  </>
                )}
                {trip.num_travelers && (
                  <>
                    <span style={{ opacity: 0.5 }}>·</span>
                    <span>{trip.num_travelers} {trip.num_travelers === 1 ? "traveler" : "travelers"}</span>
                  </>
                )}
                {trip.total_budget && (
                  <>
                    <span style={{ opacity: 0.5 }}>·</span>
                    <span style={{ fontWeight: 600, color: "var(--ink)" }}>₹{Number(trip.total_budget).toLocaleString('en-IN')}</span>
                  </>
                )}
              </div>
            </div>
            <span className={`pill ${statusPill(trip.status)}`} style={{ flexShrink: 0, marginTop: 2 }}>
              {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
            </span>
          </div>

          {/* Progress bar for ongoing */}
          {pct !== null && (
            <div style={{ marginBottom: 14 }}>
              <div style={{ height: 3, background: "var(--border)", borderRadius: 999, overflow: "hidden" }}>
                <div style={{ width: `${pct}%`, height: "100%", background: "var(--accent)", borderRadius: 999, transition: "width 0.6s ease" }} />
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--ink-soft)", marginTop: 4 }}>{pct}% complete</p>
            </div>
          )}

          {/* Stops preview */}
          {trip.stops?.length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
              {trip.stops.slice(0, 3).map((s, i) => (
                <span key={s.id} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <span style={{ fontSize: "0.8125rem", color: "var(--ink-soft)" }}>{s.city?.name}</span>
                  {i < Math.min(trip.stops.length - 1, 2) && <ArrowRight size={10} color="var(--ink-soft)" />}
                </span>
              ))}
              {trip.stops.length > 3 && (
                <span style={{ fontSize: "0.8125rem", color: "var(--ink-soft)" }}>+{trip.stops.length - 3} more</span>
              )}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}

export function TripCardSkeleton() {
  return (
    <div className="card stagger-item" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
          <div className="skeleton" style={{ height: 15, width: "65%" }} />
          <div className="skeleton" style={{ height: 12, width: "45%" }} />
        </div>
        <div className="skeleton" style={{ height: 22, width: 72, borderRadius: 999, flexShrink: 0 }} />
      </div>
      <div className="skeleton" style={{ height: 3, width: "100%", borderRadius: 999 }} />
    </div>
  );
}
