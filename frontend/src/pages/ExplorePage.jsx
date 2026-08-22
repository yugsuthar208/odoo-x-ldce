import { useState, useEffect } from "react";
import { Search, Map } from "lucide-react";
import { cityService } from "../services/cityService";
import CityCard from "../components/cities/CityCard";

const REGIONS = ["All", "Europe", "Asia", "North America", "South America", "Africa", "Oceania", "Middle East"];

export default function ExplorePage() {
  const [cities, setCities] = useState([]);
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCities();
  }, [region]); // Re-load when region changes

  // Use a debounce or just load on submit/enter for search, 
  // but for simplicity let's reload on blur or button click
  const loadCities = async () => {
    setLoading(true);
    try {
      const res = await cityService.getCities(search, region);
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
    <div className="page fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1>Explore Destinations</h1>
        <Map className="text-primary" size={28} />
      </div>

      <div className="card" style={{ padding: 16, marginBottom: 24, display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, flex: 1, minWidth: 250 }}>
          <div className="input-group" style={{ flex: 1 }}>
            <Search size={18} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)" }} />
            <input 
              type="text" 
              className="input" 
              placeholder="Search cities..." 
              style={{ paddingLeft: 36 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn--primary">Search</button>
        </form>

        <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4 }}>
          {REGIONS.map((r) => (
            <button 
              key={r}
              className={`btn btn--sm ${region === r ? "btn--primary" : "btn--secondary"}`}
              onClick={() => setRegion(r)}
              style={{ whiteSpace: "nowrap", borderRadius: "var(--radius-full)" }}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "48px 0", color: "var(--ink-soft)" }}>Loading destinations...</div>
      ) : cities.length > 0 ? (
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", 
          gap: 24 
        }}>
          {cities.map((city) => (
            <CityCard key={city.id} city={city} />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "64px 20px", background: "var(--surface)", borderRadius: "var(--radius-md)" }}>
          <p style={{ color: "var(--ink-soft)" }}>No destinations found matching your criteria.</p>
        </div>
      )}
    </div>
  );
}
