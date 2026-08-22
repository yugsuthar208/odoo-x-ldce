import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { tripService } from "../services/tripService";
import { recommendService } from "../services/recommendService";
import { TripCard, TripCardSkeleton } from "../components/trips/TripCard";
import { ErrorState } from "../components/common/ErrorState";

function CityCard({ city }) {
  return (
    <div className="card card--hover" style={{ minWidth: 200, maxWidth: 220, flexShrink: 0, overflow: "hidden", cursor: "pointer" }}>
      {city.image_url ? (
        <img src={city.image_url} alt={city.name} style={{ width: "100%", height: 120, objectFit: "cover" }} />
      ) : (
        <div style={{ width: "100%", height: 120, background: "var(--border)" }} />
      )}
      <div style={{ padding: "12px 14px" }}>
        <p style={{ fontWeight: 700, fontSize: "0.9375rem" }}>{city.name}</p>
        <p style={{ color: "var(--ink-soft)", fontSize: "0.8125rem" }}>{city.country}</p>
        <span className="pill" style={{ marginTop: 8, background: "var(--surface)", color: "var(--ink-soft)", border: "1px solid var(--border)" }}>
          ${city.cost_index}/day
        </span>
      </div>
    </div>
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

  const activeTrips = trips.filter((t) => t.status === "upcoming" || t.status === "ongoing");
  const recentTrips = trips.slice(0, 6);

  return (
    <div className="page">
      {/* Header Banner */}
      <div style={{
        background: "var(--ink)",
        color: "var(--white)",
        borderRadius: "var(--radius-card)",
        padding: "32px",
        height: "140px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "48px",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{ position: "relative", zIndex: 1 }}>
          <h1 style={{ marginBottom: 4, color: "var(--white)", fontSize: "2rem" }}>{greeting}, {firstName} ✈</h1>
          <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "1rem" }}>
            {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>
        <Link to="/trips" className="btn btn--accent" style={{ position: "relative", zIndex: 1 }}>
          <Plus size={16} /> New Trip
        </Link>
        {/* Decorative background element */}
        <div style={{
          position: "absolute",
          top: 0, right: 0, bottom: 0, width: "300px",
          background: "radial-gradient(circle at 100% 50%, rgba(195,248,50,0.1) 0%, transparent 70%)"
        }} />
      </div>

      {/* Active trips */}
      <section style={{ marginBottom: 48 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <h2>My Trips</h2>
          <Link to="/trips" style={{ fontSize: "0.875rem", color: "var(--ink-soft)", fontWeight: 500 }}>View all →</Link>
        </div>

        {tripsLoading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
            {[1,2,3].map((i) => <TripCardSkeleton key={i} />)}
          </div>
        ) : tripsError ? (
          <ErrorState message={tripsError} onRetry={() => window.location.reload()} />
        ) : recentTrips.length === 0 ? (
          <div className="card" style={{ padding: 40, textAlign: "center" }}>
            <p style={{ color: "var(--ink-soft)", marginBottom: 16 }}>No trips yet. Start planning!</p>
            <Link to="/trips" className="btn btn--accent"><Plus size={16} /> Create your first trip</Link>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
            {recentTrips.map((trip) => <TripCard key={trip.id} trip={trip} />)}
          </div>
        )}
      </section>

      {/* AI Recommended cities */}
      <section>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <Sparkles size={18} color="var(--accent)" />
          <h2>Recommended for You</h2>
        </div>
        {citiesLoading ? (
          <div style={{ display: "flex", gap: 16, overflowX: "auto", paddingBottom: 8 }}>
            {[1,2,3,4].map((i) => (
              <div key={i} className="card" style={{ minWidth: 200, maxWidth: 220, flexShrink: 0 }}>
                <div className="skeleton" style={{ width: "100%", height: 120, borderRadius: "var(--radius-card) var(--radius-card) 0 0" }} />
                <div style={{ padding: "12px 14px", display: "flex", flexDirection: "column", gap: 8 }}>
                  <div className="skeleton" style={{ height: 14, width: "70%" }} />
                  <div className="skeleton" style={{ height: 12, width: "50%" }} />
                </div>
              </div>
            ))}
          </div>
        ) : cities.length > 0 ? (
          <div style={{ display: "flex", gap: 16, overflowX: "auto", paddingBottom: 8 }}>
            {cities.map((city) => <CityCard key={city.id} city={city} />)}
          </div>
        ) : (
          <Link to="/explore" className="btn btn--ghost">Browse destinations →</Link>
        )}
      </section>
    </div>
  );
}
