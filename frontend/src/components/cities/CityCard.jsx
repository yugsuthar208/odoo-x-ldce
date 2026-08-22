import { MapPin, TrendingUp, DollarSign } from "lucide-react";

export default function CityCard({ city }) {
  return (
    <div className="card card--hover" style={{ display: "flex", flexDirection: "column", height: "100%", borderRadius: "24px", overflow: "hidden", border: "1px solid rgba(0,0,0,0.05)", cursor: "pointer" }}>
      <div 
        style={{ 
          height: 200, 
          background: `url(${city.image_url || "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800"}) center/cover`,
          position: "relative",
          transition: "transform 0.5s ease"
        }}
        className="city-img-hover"
      >
        <div style={{
          position: "absolute", top: 16, right: 16, 
          background: "rgba(255,255,255,0.9)", 
          backdropFilter: "blur(4px)",
          color: "#000", 
          padding: "6px 12px", borderRadius: "99px",
          fontSize: "0.75rem", fontWeight: "700",
          display: "flex", alignItems: "center", gap: 4,
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
        }}>
          <TrendingUp size={14} color="#000" /> {city.popularity_score}/10
        </div>
      </div>
      <div style={{ padding: 24, flex: 1, display: "flex", flexDirection: "column", background: "#fff" }}>
        <h3 style={{ fontSize: "1.4rem", marginBottom: 6, fontWeight: 700, letterSpacing: "-0.5px" }}>{city.name}</h3>
        <p style={{ color: "var(--ink-soft)", display: "flex", alignItems: "center", gap: 6, marginBottom: 16, fontSize: "0.9rem", fontWeight: 500 }}>
          <MapPin size={14} /> {city.country} {city.region ? `• ${city.region}` : ""}
        </p>
        <p style={{ fontSize: "0.95rem", color: "rgba(0,0,0,0.6)", marginBottom: 20, flex: 1, lineHeight: 1.5 }}>
          {city.description || "A beautiful destination to explore."}
        </p>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 20, borderTop: "1px solid rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--ink)", fontWeight: "700", fontSize: "1.1rem" }}>
            <span>₹ {Math.round((city.cost_index || 50) * 40).toLocaleString('en-IN')}</span> 
            <span style={{ fontSize: "0.75rem", color: "var(--ink-soft)", fontWeight: "normal" }}>/ night stay avg</span>
          </div>
        </div>
      </div>
    </div>
  );
}
