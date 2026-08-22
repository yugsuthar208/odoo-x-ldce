import { useState, useEffect } from "react";
import { X, Search, DollarSign, Clock } from "lucide-react";
import { cityService } from "../../services/cityService";
import { tripService } from "../../services/tripService";
import { LoadingSpinner } from "../common/LoadingSpinner";

export function ActivityPickerModal({ tripId, stopId, cityId, onClose, onAdded }) {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(null); // id of activity being saved

  useEffect(() => {
    if (!cityId) return;
    cityService.getCityActivities(cityId)
      .then(r => {
        const list = r?.data || (Array.isArray(r) ? r : []);
        setActivities(Array.isArray(list) ? list : []);
      })
      .catch(() => setActivities([]))
      .finally(() => setLoading(false));
  }, [cityId]);

  const handleAdd = async (activity) => {
    setSaving(activity.id);
    try {
      await onAdded(activity, stopId);
    } finally {
      setSaving(null);
    }
  };

  const filtered = activities.filter(a => a.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)" }} onClick={onClose} />
      <div className="card animate-fadeUp" style={{ position: "relative", zIndex: 1, width: "min(600px, 92vw)", height: "80vh", padding: 32, display: "flex", flexDirection: "column" }}>
        
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
          <h2>Add Activity</h2>
          <button className="btn btn--icon btn--ghost" onClick={onClose}><X size={18} /></button>
        </div>

        <div style={{ position: "relative", marginBottom: 24 }}>
          <Search size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)" }} />
          <input
            className="input" placeholder="Search activities..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: 42 }} autoFocus
          />
        </div>

        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 12 }}>
          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: 48 }}><LoadingSpinner size={32} /></div>
          ) : filtered.length === 0 ? (
            <p style={{ textAlign: "center", color: "var(--ink-soft)", padding: 48 }}>No activities found.</p>
          ) : (
            filtered.map(act => (
              <div key={act.id} className="card card--hover" style={{ padding: 16, display: "flex", gap: 16 }}>
                {act.image_url ? (
                  <img src={act.image_url} alt="" style={{ width: 80, height: 80, borderRadius: 8, objectFit: "cover" }} />
                ) : <div style={{ width: 80, height: 80, borderRadius: 8, background: "var(--surface)" }} />}
                
                <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <h4 style={{ margin: 0, fontSize: "1rem" }}>{act.name}</h4>
                      <span className={`pill pill--${act.category.toLowerCase()}`}>{act.category}</span>
                    </div>
                    <p style={{ fontSize: "0.8125rem", color: "var(--ink-soft)", margin: "4px 0 0", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                      {act.description}
                    </p>
                  </div>
                  
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 12 }}>
                    <div style={{ display: "flex", gap: 16, color: "var(--ink-soft)", fontSize: "0.8125rem", fontWeight: 500 }}>
                      <span style={{ display: "flex", alignItems: "center", gap: 2, fontWeight: 600, color: "var(--accent)" }}>₹{Number(act.estimated_cost || 0).toLocaleString('en-IN')}</span>
                      <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Clock size={14} /> {act.duration_hours}h</span>
                    </div>
                    <button className="btn btn--sm btn--primary" onClick={() => handleAdd(act)} disabled={saving === act.id}>
                      {saving === act.id ? <LoadingSpinner size={14} color="#fff" /> : "Add"}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}
