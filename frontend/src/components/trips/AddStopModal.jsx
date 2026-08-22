import { useState, useEffect } from "react";
import { X, Search } from "lucide-react";
import { cityService } from "../../services/cityService";
import { LoadingSpinner } from "../common/LoadingSpinner";

export function AddStopModal({ onClose, onAdd }) {
  const [search, setSearch] = useState("");
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCity, setSelectedCity] = useState(null);

  const [form, setForm] = useState({ arrival_date: "", departure_date: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (search.length < 2) {
      setCities([]);
      return;
    }
    const delay = setTimeout(() => {
      setLoading(true);
      cityService.getCities(search)
        .then(r => setCities(r.data))
        .catch(() => setCities([]))
        .finally(() => setLoading(false));
    }, 400);
    return () => clearTimeout(delay);
  }, [search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCity) return;
    setSaving(true);
    await onAdd({
      city_id: selectedCity.id,
      arrival_date: form.arrival_date,
      departure_date: form.departure_date,
    });
    setSaving(false);
  };

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)" }} onClick={onClose} />
      <div className="card animate-fadeUp" style={{ position: "relative", zIndex: 1, width: "min(480px, 92vw)", padding: 32, maxHeight: "90vh", display: "flex", flexDirection: "column" }}>
        
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
          <h2>Add Destination</h2>
          <button className="btn btn--icon btn--ghost" onClick={onClose}><X size={18} /></button>
        </div>

        {!selectedCity ? (
          <div style={{ flex: 1, overflowY: "auto" }}>
            <div style={{ position: "relative", marginBottom: 16 }}>
              <Search size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)" }} />
              <input
                className="input" placeholder="Search cities..."
                value={search} onChange={(e) => setSearch(e.target.value)}
                style={{ paddingLeft: 42 }} autoFocus
              />
              {loading && <div style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)" }}><LoadingSpinner size={14} color="var(--ink-soft)" /></div>}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {cities.map(city => (
                <div key={city.id} className="card card--hover" style={{ padding: "12px 16px", cursor: "pointer", display: "flex", alignItems: "center", gap: 12 }} onClick={() => setSelectedCity(city)}>
                  {city.image_url ? (
                    <img src={city.image_url} alt="" style={{ width: 40, height: 40, borderRadius: 8, objectFit: "cover" }} />
                  ) : <div style={{ width: 40, height: 40, borderRadius: 8, background: "var(--surface)" }} />}
                  <div>
                    <h4 style={{ margin: 0 }}>{city.name}</h4>
                    <p style={{ fontSize: "0.8125rem", color: "var(--ink-soft)", margin: 0 }}>{city.country}</p>
                  </div>
                </div>
              ))}
              {search.length >= 2 && !loading && cities.length === 0 && (
                <p style={{ textAlign: "center", color: "var(--ink-soft)", padding: 24 }}>No cities found.</p>
              )}
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, background: "var(--surface)", borderRadius: "var(--radius-input)", marginBottom: 8 }}>
              <button type="button" className="btn btn--icon btn--ghost" onClick={() => setSelectedCity(null)}><X size={14} /></button>
              <h4 style={{ margin: 0 }}>{selectedCity.name}, {selectedCity.country}</h4>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label className="label">Arrival Date *</label>
                <input className="input" type="date" value={form.arrival_date} onChange={e => setForm({...form, arrival_date: e.target.value})} required />
              </div>
              <div>
                <label className="label">Departure Date *</label>
                <input className="input" type="date" value={form.departure_date} onChange={e => setForm({...form, departure_date: e.target.value})} required />
              </div>
            </div>

            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 16 }}>
              <button type="button" className="btn btn--ghost" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn--primary" disabled={saving}>
                {saving ? <LoadingSpinner size={14} color="#fff" /> : "Add to Trip"}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
