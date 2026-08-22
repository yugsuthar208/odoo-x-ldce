import { MapPin, TrendingUp, DollarSign } from "lucide-react";

export default function CityCard({ city }) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div 
        style={{ 
          height: 180, 
          background: `url(${city.image_url || "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800"}) center/cover`,
          borderTopLeftRadius: "var(--radius-md)",
          borderTopRightRadius: "var(--radius-md)",
          position: "relative"
        }}
      >
        <div style={{
          position: "absolute", top: 12, right: 12, 
          background: "rgba(0,0,0,0.6)", color: "white", 
          padding: "4px 8px", borderRadius: "var(--radius-full)",
          fontSize: "0.75rem", fontWeight: "600",
          display: "flex", alignItems: "center", gap: 4
        }}>
          <TrendingUp size={14} /> {city.popularity_score}/10
        </div>
      </div>
      <div style={{ padding: 16, flex: 1, display: "flex", flexDirection: "column" }}>
        <h3 style={{ fontSize: "1.125rem", marginBottom: 4 }}>{city.name}</h3>
        <p style={{ color: "var(--ink-soft)", display: "flex", alignItems: "center", gap: 4, marginBottom: 12, fontSize: "0.875rem" }}>
          <MapPin size={14} /> {city.country} {city.region ? `• ${city.region}` : ""}
        </p>
        <p style={{ fontSize: "0.875rem", color: "var(--ink-medium)", marginBottom: 16, flex: 1 }}>
          {city.description || "A beautiful destination to explore."}
        </p>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 16, borderTop: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--primary-main)", fontWeight: "500" }}>
            <DollarSign size={16} /> {city.cost_index} <span style={{ fontSize: "0.75rem", color: "var(--ink-soft)" }}>Cost Index</span>
          </div>
        </div>
      </div>
    </div>
  );
}
