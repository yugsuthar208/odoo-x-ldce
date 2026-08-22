import { CloudSun, Navigation, Plus } from "lucide-react";

export function StopDetailBar({ selectedStop, nextStop, onAddActivity }) {
  if (!selectedStop) return null;

  // Basic mock weather (in a real app, you'd call Open-Meteo here using selectedStop.city.latitude/longitude)
  const weather = "☀️ 24°C";

  return (
    <div style={{
      position: "absolute", bottom: 20, left: 20, right: 20, zIndex: 1000,
      background: "var(--white)",
      borderRadius: "var(--radius-card)",
      padding: "16px 20px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      boxShadow: "var(--shadow-float)",
      border: "1px solid var(--border)",
    }} className="animate-fadeUp">
      
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <div>
          <h3 style={{ fontSize: "1.125rem", marginBottom: 2 }}>{selectedStop.city?.name || selectedStop.city_name || "Destination"}</h3>
          <p style={{ fontSize: "0.8125rem", color: "var(--ink-soft)" }}>
            {selectedStop.arrival_date} → {selectedStop.departure_date}
          </p>
        </div>

        <div style={{ display: "flex", gap: 12 }}>
          <div className="pill" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}>
            <CloudSun size={14} color="var(--ink-soft)" /> {weather}
          </div>
          {nextStop && (
            <div className="pill" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--ink)" }}>
              <Navigation size={14} color="var(--accent)" /> To {nextStop.city?.name || nextStop.city_name || "Next Stop"}
            </div>
          )}
        </div>
      </div>

      <button className="btn btn--accent" onClick={onAddActivity}>
        <Plus size={16} /> Add Activity
      </button>

    </div>
  );
}
