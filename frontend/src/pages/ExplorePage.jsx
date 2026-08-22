import { useState, useEffect } from "react";
import { Search, Map, Compass } from "lucide-react";
import { cityService } from "../services/cityService";
import CityCard from "../components/cities/CityCard";
import { motion } from "framer-motion";

const REGIONS = [
  "All India",
  "North India (Himalayas)",
  "West & Rajasthan",
  "South India & Western Ghats",
  "East & Northeast",
  "Central & Spiritual"
];

export default function ExplorePage() {
  const [cities, setCities] = useState([]);
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("All India");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCities();
  }, [region]);

  const loadCities = async () => {
    setLoading(true);
    try {
      const regionParam = (region === "All India" || region === "All") ? undefined : region;
      const res = await cityService.getCities(search, regionParam);
      const list = res?.data || (Array.isArray(res) ? res : []);
      setCities(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error("Failed to load cities", err);
      setCities([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadCities();
  };

  return (
    <motion.div 
      className="page"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: "2.5rem", letterSpacing: "-1px", marginBottom: "8px" }}>Explore Destinations</h1>
          <p style={{ color: "var(--ink-soft)", fontSize: "1.1rem" }}>Find your next adventure from our curated list of global cities.</p>
        </div>
      </div>

      <div style={{
        background: "var(--white)",
        padding: "24px",
        borderRadius: "24px",
        boxShadow: "0 10px 40px rgba(0,0,0,0.05)",
        marginBottom: "48px",
        display: "flex",
        gap: "16px",
        alignItems: "center",
        flexWrap: "wrap",
        border: "1px solid rgba(0,0,0,0.03)"
      }}>
        <form onSubmit={handleSearch} style={{ flex: 1, minWidth: 300, position: "relative" }}>
          <Search size={20} style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)" }} />
          <input
            type="text"
            placeholder="Search by city, country, or vibe..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: "100%",
              padding: "16px 16px 16px 48px",
              borderRadius: "16px",
              border: "1px solid var(--border)",
              background: "var(--surface)",
              fontSize: "1rem",
              transition: "all 0.3s ease"
            }}
          />
        </form>
        
        <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "4px" }}>
          {REGIONS.map(r => (
            <button
              key={r}
              onClick={() => setRegion(r)}
              style={{
                padding: "12px 20px",
                borderRadius: "99px",
                background: region === r ? "var(--ink)" : "var(--surface)",
                color: region === r ? "var(--white)" : "var(--ink)",
                border: `1px solid ${region === r ? "var(--ink)" : "var(--border)"}`,
                cursor: "pointer",
                whiteSpace: "nowrap",
                fontWeight: 500,
                transition: "all 0.3s ease"
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "64px" }}>
          <div className="spinner" style={{ width: 40, height: 40, border: "3px solid var(--border)", borderTopColor: "var(--ink)", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
        </div>
      ) : cities.length === 0 ? (
        <div style={{ padding: "80px", textAlign: "center", background: "rgba(0,0,0,0.02)", borderRadius: "24px", border: "1px dashed rgba(0,0,0,0.1)" }}>
          <Compass size={48} style={{ margin: "0 auto", marginBottom: 16, opacity: 0.2 }} />
          <h2 style={{ marginBottom: 8 }}>No destinations found</h2>
          <p style={{ color: "var(--ink-soft)" }}>Try adjusting your search or region filter.</p>
        </div>
      ) : (
        <motion.div 
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "24px" }}
          initial="hidden"
          animate="show"
          variants={{
            hidden: { opacity: 0 },
            show: { opacity: 1, transition: { staggerChildren: 0.05 } }
          }}
        >
          {cities.map((city) => (
            <motion.div key={city.id} variants={{
              hidden: { opacity: 0, scale: 0.9 },
              show: { opacity: 1, scale: 1, transition: { duration: 0.4 } }
            }}>
              <CityCard city={city} />
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
