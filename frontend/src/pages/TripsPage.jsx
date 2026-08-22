import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, X } from "lucide-react";
import { tripService } from "../services/tripService";
import { cityService } from "../services/cityService";
import { TripCard, TripCardSkeleton } from "../components/trips/TripCard";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { useToast } from "../components/common/Toast";

const TABS = ["all", "upcoming", "ongoing", "completed", "draft"];

const INDIAN_ORIGIN_CITIES = [
  "Mumbai", "Delhi", "Bengaluru", "Ahmedabad", "Pune", "Jaipur", 
  "Kolkata", "Chennai", "Hyderabad", "Surat", "Chandigarh", "Lucknow", "Indore", "Kochi"
];

function TripCreateModal({ onClose, onCreated }) {
  const { addToast } = useToast();
  const [form, setForm] = useState({
    title: "", 
    description: "", 
    start_date: "", 
    end_date: "",
    origin_city: "Mumbai",
    num_travelers: 1,
    transit_mode: "train",
    total_budget: "", 
    currency: "INR", 
    visibility: "private", 
    status: "draft",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const set = (f) => (e) => setForm((p) => ({ ...p, [f]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    if (form.start_date > form.end_date) { setError("End date must be after start date"); return; }
    setError(""); setLoading(true);
    try {
      const payload = {
        ...form,
        num_travelers: parseInt(form.num_travelers) || 1,
        total_budget: form.total_budget ? parseFloat(form.total_budget) : null,
      };
      const res = await tripService.createTrip(payload);
      addToast({ message: "Trip created successfully!" });
      onCreated(res.data);
    } catch (err) {
      setError(err.message);
      addToast({ message: err.message, type: "error" });
    } finally { setLoading(false); }
  }

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)" }} onClick={onClose} />
      <div className="card animate-fadeUp" style={{ position: "relative", zIndex: 1, width: "min(560px, 92vw)", padding: 32, maxHeight: "90vh", overflowY: "auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <div>
            <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Tripora Bharat</span>
            <h2 style={{ marginTop: 2 }}>Plan a New Journey</h2>
          </div>
          <button className="btn btn--icon btn--ghost" onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label className="label" htmlFor="ct-title">Trip Title *</label>
            <input id="ct-title" className="input" value={form.title} onChange={set("title")} placeholder="e.g. Royal Rajasthan Heritage Trail" required />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 12 }}>
            <div>
              <label className="label" htmlFor="ct-origin">Starting City (Origin) *</label>
              <select id="ct-origin" className="input" value={form.origin_city} onChange={set("origin_city")}>
                {INDIAN_ORIGIN_CITIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="ct-travelers">Travelers / Group Size</label>
              <input id="ct-travelers" className="input" type="number" min="1" max="50" value={form.num_travelers} onChange={set("num_travelers")} required />
            </div>
          </div>

          <div>
            <label className="label" htmlFor="ct-desc">Description</label>
            <textarea id="ct-desc" className="input" rows={2} value={form.description} onChange={set("description")} placeholder="Trip notes, local thali wishlist, or group goals..." />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label className="label" htmlFor="ct-start">Start Date *</label>
              <input id="ct-start" className="input" type="date" value={form.start_date} onChange={set("start_date")} required />
            </div>
            <div>
              <label className="label" htmlFor="ct-end">End Date *</label>
              <input id="ct-end" className={`input ${form.start_date && form.end_date && form.end_date < form.start_date ? "input--error" : ""}`} type="date" value={form.end_date} onChange={set("end_date")} required />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 12 }}>
            <div>
              <label className="label" htmlFor="ct-budget">Total Budget (₹ INR)</label>
              <input id="ct-budget" className="input" type="number" value={form.total_budget} onChange={set("total_budget")} placeholder="25000" min="0" />
            </div>
            <div>
              <label className="label" htmlFor="ct-vis">Visibility</label>
              <select id="ct-vis" className="input" value={form.visibility} onChange={set("visibility")}>
                <option value="private">Private</option>
                <option value="public">Public</option>
                <option value="friends">Friends</option>
              </select>
            </div>
          </div>
          {error && <p style={{ color: "var(--danger)", fontSize: "0.875rem" }}>{error}</p>}
          <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
            <button type="button" className="btn btn--ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn--primary" disabled={loading}>
              {loading ? <LoadingSpinner size={14} color="#fff" /> : "Create Trip"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function TripsPage() {
  const navigate = useNavigate();
  const [trips, setTrips]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [tab, setTab]       = useState("all");
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    tripService.getTrips()
      .then((r) => { setTrips(r.data || []); setError(null); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = trips.filter((t) => {
    const matchTab    = tab === "all" || t.status === tab;
    const matchSearch = !search || t.title.toLowerCase().includes(search.toLowerCase());
    return matchTab && matchSearch;
  });

  return (
    <div className="page">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <h1>My Trips</h1>
        <button className="btn btn--accent" onClick={() => setShowModal(true)}>
          <Plus size={16} /> New Trip
        </button>
      </div>

      {/* Search */}
      <div style={{ position: "relative", marginBottom: 20 }}>
        <Search size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)" }} />
        <input
          className="input"
          placeholder="Search trips..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ paddingLeft: 42 }}
        />
        {search && (
          <button style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)", background: "none", border: "none", cursor: "pointer" }} onClick={() => setSearch("")}>
            <X size={14} />
          </button>
        )}
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 24, flexWrap: "wrap" }}>
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`btn btn--sm ${tab === t ? "btn--primary" : "btn--ghost"}`}
            style={{ textTransform: "capitalize" }}
          >{t}</button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: 24 }}>
          {[1,2,3,4,5,6].map((i) => <TripCardSkeleton key={i} />)}
        </div>
      ) : error ? (
        <ErrorState message={error} onRetry={load} />
      ) : filtered.length === 0 ? (
        <div className="card" style={{ padding: 64, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <div style={{ marginBottom: 24, position: "relative" }}>
            <svg width="120" height="80" viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 60 C 40 60, 40 20, 60 20 C 80 20, 80 60, 100 60" stroke="var(--border)" strokeWidth="3" strokeDasharray="6 6" fill="none" />
              <circle cx="20" cy="60" r="6" fill="var(--ink)" />
              <circle cx="60" cy="20" r="6" fill="var(--warn)" />
              <path d="M100 60 C 100 60, 100 40, 100 40" stroke="var(--accent)" strokeWidth="3" />
              <circle cx="100" cy="60" r="6" fill="var(--accent)" />
            </svg>
          </div>
          <p style={{ color: "var(--ink-soft)", marginBottom: 24, fontSize: "1.125rem" }}>
            {search ? `No trips matching "${search}"` : `No ${tab === "all" ? "" : tab + " "}trips yet.`}
          </p>
          {!search && (
            <button className="btn btn--accent" onClick={() => setShowModal(true)}>
              <Plus size={16} /> Plan your first trip
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: 24 }}>
          {filtered.map((trip) => <TripCard key={trip.id} trip={trip} />)}
        </div>
      )}

      {showModal && (
        <TripCreateModal
          onClose={() => setShowModal(false)}
          onCreated={(trip) => { setShowModal(false); navigate(`/trips/${trip.id}`); }}
        />
      )}
    </div>
  );
}
