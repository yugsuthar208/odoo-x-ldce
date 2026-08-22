import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Sparkles, MapPin, Compass, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { tripService } from "../services/tripService";
import { recommendService } from "../services/recommendService";
import { TripCard, TripCardSkeleton } from "../components/trips/TripCard";
import { ErrorState } from "../components/common/ErrorState";
import { motion } from "framer-motion";

function CityCard({ city }) {
  return (
    <motion.div 
      className="card card--hover" 
      whileHover={{ y: -5, boxShadow: "0 10px 30px rgba(0,0,0,0.1)" }}
      style={{ 
        minWidth: 220, 
        maxWidth: 240, 
        flexShrink: 0, 
        overflow: "hidden", 
        cursor: "pointer",
        borderRadius: "20px",
        border: "1px solid rgba(0,0,0,0.05)"
      }}
    >
      <div style={{ position: "relative" }}>
        {city.image_url ? (
          <img src={city.image_url} alt={city.name} style={{ width: "100%", height: 160, objectFit: "cover" }} />
        ) : (
          <div style={{ width: "100%", height: 160, background: "var(--border)" }} />
        )}
        <div style={{
          position: "absolute", top: 12, right: 12,
          background: "rgba(255,255,255,0.9)",
          backdropFilter: "blur(4px)",
          padding: "4px 8px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: 600,
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}>
          ★ {city.popularity_score || 9.5}
        </div>
      </div>
      <div style={{ padding: "16px" }}>
        <p style={{ fontWeight: 700, fontSize: "1.1rem", marginBottom: "4px" }}>{city.name}</p>
        <p style={{ color: "var(--ink-soft)", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "4px" }}>
          <MapPin size={12} /> {city.country}
        </p>
        <div style={{ marginTop: 12, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontWeight: 600, color: "var(--ink)", fontSize: "0.9rem" }}>
            ${city.cost_index}/day
          </span>
          <ArrowRight size={16} color="var(--ink-soft)" />
        </div>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [trips, setTrips]     = useState([]);
  const [cities, setCities]   = useState([]);
  const [tripsLoading, setTripsLoading]   = useState(true);
  const [citiesLoading, setCitiesLoading] = useState(true);
  const [tripsError, setTripsError]       = useState(null);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const firstName = user?.full_name?.split(" ")[0] || "Traveler";

  useEffect(() => {
    tripService.getTrips()
      .then((r) => setTrips(r.data || []))
      .catch((e) => setTripsError(e.message))
      .finally(() => setTripsLoading(false));

    recommendService.getRecommendedCities()
      .then((r) => setCities(r.data || []))
      .catch(() => {})
      .finally(() => setCitiesLoading(false));
  }, []);

  const recentTrips = trips.slice(0, 6);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
  };

  return (
    <motion.div 
      className="page"
      variants={containerVariants}
      initial="hidden"
      animate="show"
      style={{ maxWidth: "1200px", margin: "0 auto", padding: "40px 20px" }}
    >
      {/* Header Banner */}
      <motion.div 
        variants={itemVariants}
        style={{
          background: "linear-gradient(135deg, #111, #222)",
          color: "var(--white)",
          borderRadius: "30px",
          padding: "48px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "56px",
          position: "relative",
          overflow: "hidden",
          boxShadow: "0 20px 40px rgba(0,0,0,0.15)"
        }}
      >
        <div style={{ position: "relative", zIndex: 1 }}>
          <h1 style={{ marginBottom: 8, color: "var(--white)", fontSize: "2.5rem", fontWeight: 400, letterSpacing: "-1px" }}>
            {greeting}, <span style={{ fontWeight: 700 }}>{firstName}</span>
          </h1>
          <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "1.1rem" }}>
            {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} style={{ position: "relative", zIndex: 1 }}>
          <Link to="/trips" className="btn" style={{ 
            background: "#fff", 
            color: "#000", 
            padding: "16px 24px", 
            borderRadius: "999px",
            fontWeight: 600,
            display: "flex",
            gap: "8px",
            alignItems: "center"
          }}>
            <Plus size={18} /> Plan a new trip
          </Link>
        </motion.div>
        {/* Decorative background elements */}
        <div style={{
          position: "absolute",
          top: "-50%", right: "-10%",
          width: "500px", height: "500px",
          background: "radial-gradient(circle, rgba(195,248,50,0.15) 0%, transparent 70%)",
          filter: "blur(40px)"
        }} />
      </motion.div>

      {/* Active trips */}
      <motion.section variants={itemVariants} style={{ marginBottom: 64 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
          <h2 style={{ fontSize: "1.8rem", letterSpacing: "-0.5px" }}>Your upcoming journeys</h2>
          <Link to="/trips" style={{ fontSize: "0.9rem", color: "var(--ink)", fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
            View all <ArrowRight size={14} />
          </Link>
        </div>

        {tripsLoading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 24 }}>
            {[1,2,3].map((i) => <TripCardSkeleton key={i} />)}
          </div>
        ) : tripsError ? (
          <ErrorState message={tripsError} onRetry={() => window.location.reload()} />
        ) : recentTrips.length === 0 ? (
          <div className="card" style={{ padding: 60, textAlign: "center", borderRadius: "24px", background: "rgba(0,0,0,0.02)", border: "1px dashed rgba(0,0,0,0.1)" }}>
            <Compass size={40} style={{ margin: "0 auto", marginBottom: 16, opacity: 0.3 }} />
            <h3 style={{ marginBottom: 8 }}>No trips planned yet</h3>
            <p style={{ color: "var(--ink-soft)", marginBottom: 24 }}>Your itinerary dashboard is waiting for your next adventure.</p>
            <Link to="/trips" className="btn btn--accent"><Plus size={16} /> Create your first trip</Link>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 24 }}>
            {recentTrips.map((trip) => (
              <motion.div key={trip.id} whileHover={{ y: -5 }}>
                <TripCard trip={trip} />
              </motion.div>
            ))}
          </div>
        )}
      </motion.section>

      {/* AI Recommended cities */}
      <motion.section variants={itemVariants}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
          <div style={{ background: "rgba(195,248,50,0.2)", padding: "8px", borderRadius: "12px" }}>
            <Sparkles size={20} color="#8aab00" />
          </div>
          <h2 style={{ fontSize: "1.8rem", letterSpacing: "-0.5px" }}>AI Recommendations for You</h2>
        </div>
        
        {citiesLoading ? (
          <div style={{ display: "flex", gap: 24, overflowX: "auto", paddingBottom: 16 }}>
            {[1,2,3,4].map((i) => (
              <div key={i} className="card" style={{ minWidth: 220, maxWidth: 240, flexShrink: 0, borderRadius: "20px" }}>
                <div className="skeleton" style={{ width: "100%", height: 160, borderRadius: "20px 20px 0 0" }} />
                <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: 12 }}>
                  <div className="skeleton" style={{ height: 16, width: "70%" }} />
                  <div className="skeleton" style={{ height: 12, width: "50%" }} />
                </div>
              </div>
            ))}
          </div>
        ) : cities.length > 0 ? (
          <div style={{ 
            display: "flex", 
            gap: 24, 
            overflowX: "auto", 
            paddingBottom: 24,
            scrollSnapType: "x mandatory",
            WebkitOverflowScrolling: "touch"
          }}>
            {cities.map((city) => (
              <div key={city.id} style={{ scrollSnapAlign: "start" }}>
                <CityCard city={city} />
              </div>
            ))}
          </div>
        ) : (
          <Link to="/explore" className="btn btn--ghost">Browse destinations <ArrowRight size={14} /></Link>
        )}
      </motion.section>
    </motion.div>
  );
}
