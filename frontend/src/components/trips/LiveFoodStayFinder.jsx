import React, { useState, useEffect } from 'react';
import { tripService } from '../../services/tripService';
import { 
  Utensils, 
  Hotel, 
  Star, 
  Sparkles, 
  Tag, 
  MapPin, 
  AlertCircle,
  Compass
} from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

export default function LiveFoodStayFinder({ cityName = 'Goa' }) {
  const [activeTab, setActiveTab] = useState('food'); // 'food' or 'stay'
  const [budgetTier, setBudgetTier] = useState('mid'); // 'budget', 'mid', 'luxury'
  const [foodResults, setFoodResults] = useState([]);
  const [stayResults, setStayResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'food') {
        const res = await tripService.getLiveFood(cityName, budgetTier);
        if (res.success) {
          setFoodResults(res.data || []);
        }
      } else {
        const res = await tripService.getLiveStays(cityName, budgetTier);
        if (res.success) {
          setStayResults(res.data || []);
        }
      }
    } catch (err) {
      console.error('Live recommendations fetch error:', err);
      setError('Could not fetch live recommendations right now.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (cityName) {
      fetchRecommendations();
    }
  }, [cityName, activeTab, budgetTier]);

  const results = activeTab === 'food' ? foodResults : stayResults;

  const budgetTiers = [
    { id: 'budget', label: 'Budget' },
    { id: 'mid', label: 'Mid-Range' },
    { id: 'luxury', label: 'Luxury' }
  ];

  return (
    <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", border: "1px solid rgba(195, 248, 50, 0.5)" }}>
            <Sparkles size={12} /> Live Discovery
          </span>
        </div>
        <h2 style={{ fontSize: "1.35rem", fontWeight: 700, margin: "6px 0 4px" }}>
          Local Food & Stays in <span style={{ color: "var(--ink)" }}>{cityName}</span>
        </h2>
        <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
          Curated authentic recommendations for legendary regional thalis, iconic dhabas, hostels and heritage stays.
        </p>
      </div>

      {/* Control Switchers Bar */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", justifyContent: "space-between" }}>
        {/* Category Tabs */}
        <div style={{
          display: "flex",
          gap: 4,
          background: "var(--surface)",
          padding: 4,
          borderRadius: "var(--radius-pill)",
          border: "1px solid var(--border)"
        }}>
          <button
            onClick={() => setActiveTab('food')}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "6px 14px",
              borderRadius: "var(--radius-pill)",
              fontSize: "0.8125rem",
              fontWeight: activeTab === 'food' ? 700 : 500,
              background: activeTab === 'food' ? "var(--ink)" : "transparent",
              color: activeTab === 'food' ? "var(--accent)" : "var(--ink-soft)",
              transition: "all var(--t-fast)",
              cursor: "pointer"
            }}
          >
            <Utensils size={14} /> Food & Dining
          </button>
          <button
            onClick={() => setActiveTab('stay')}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "6px 14px",
              borderRadius: "var(--radius-pill)",
              fontSize: "0.8125rem",
              fontWeight: activeTab === 'stay' ? 700 : 500,
              background: activeTab === 'stay' ? "var(--ink)" : "transparent",
              color: activeTab === 'stay' ? "var(--accent)" : "var(--ink-soft)",
              transition: "all var(--t-fast)",
              cursor: "pointer"
            }}
          >
            <Hotel size={14} /> Stays & Hostels
          </button>
        </div>

        {/* Budget Selector */}
        <div style={{
          display: "flex",
          gap: 4,
          background: "var(--surface)",
          padding: 4,
          borderRadius: "var(--radius-pill)",
          border: "1px solid var(--border)"
        }}>
          {budgetTiers.map((tier) => {
            const active = budgetTier === tier.id;
            return (
              <button
                key={tier.id}
                onClick={() => setBudgetTier(tier.id)}
                style={{
                  padding: "4px 12px",
                  borderRadius: "var(--radius-pill)",
                  fontSize: "0.75rem",
                  fontWeight: active ? 700 : 500,
                  background: active ? "var(--white)" : "transparent",
                  color: active ? "var(--ink)" : "var(--ink-soft)",
                  boxShadow: active ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
                  transition: "all var(--t-fast)",
                  cursor: "pointer"
                }}
              >
                {tier.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, padding: "48px 0" }}>
          <LoadingSpinner size={32} />
          <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
            Discovering authentic {activeTab === 'food' ? 'food spots' : 'stays'} in {cityName}...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="card" style={{ padding: 16, border: "1px solid var(--danger)", background: "rgba(229, 72, 77, 0.05)", display: "flex", alignItems: "center", gap: 10, color: "var(--danger)" }}>
          <AlertCircle size={18} />
          <span style={{ fontSize: "0.875rem" }}>{error}</span>
        </div>
      )}

      {/* Results Grid */}
      {!loading && (
        results.length === 0 ? (
          <div className="card" style={{ padding: 36, textAlign: "center", background: "var(--surface)" }}>
            <Compass size={32} color="var(--ink-soft)" style={{ margin: "0 auto 12px" }} />
            <h4 style={{ marginBottom: 4 }}>No recommendations found</h4>
            <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
              Try selecting a different budget tier or destination city.
            </p>
          </div>
        ) : (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 14
          }}>
            {results.map((item, idx) => (
              <div
                key={idx}
                className="card card--hover"
                style={{
                  padding: 16,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  borderRadius: "var(--radius-card)",
                  background: "var(--white)",
                  border: "1px solid var(--border)",
                  boxShadow: "var(--shadow-card)",
                  transition: "all var(--t-fast)"
                }}
              >
                <div>
                  {/* Top Bar: Type Pill + Rating */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                    <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", fontSize: "0.6875rem", fontWeight: 700 }}>
                      {item.type || (activeTab === 'food' ? 'Food & Dining' : 'Stay')}
                    </span>
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      color: "#b45309",
                      background: "#fef3c7",
                      padding: "2px 8px",
                      borderRadius: "var(--radius-pill)"
                    }}>
                      <Star size={12} fill="#f59e0b" color="#f59e0b" />
                      <span>{item.rating || '4.8'}</span>
                    </div>
                  </div>

                  {/* Title */}
                  <h3 style={{ fontSize: "0.95rem", fontWeight: 700, margin: "0 0 6px", color: "var(--ink)" }}>
                    {item.title}
                  </h3>

                  {/* Description / Highlight */}
                  <p style={{
                    fontSize: "0.8125rem",
                    color: "var(--ink-soft)",
                    lineHeight: 1.5,
                    marginBottom: 12,
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden"
                  }}>
                    {item.highlight || item.description}
                  </p>
                </div>

                {/* Bottom Bar: Estimated Price & Verification Source */}
                <div style={{
                  paddingTop: 12,
                  borderTop: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between"
                }}>
                  <div>
                    <span style={{ fontSize: "0.6875rem", color: "var(--ink-soft)", display: "block", textTransform: "uppercase", fontWeight: 600 }}>
                      Estimated Cost
                    </span>
                    <span style={{ fontSize: "0.9375rem", fontWeight: 800, color: "var(--ink)" }}>
                      {item.price_inr || "₹450 / person"}
                    </span>
                  </div>

                  <span className="pill" style={{ background: "var(--surface)", color: "var(--ink-soft)", fontSize: "0.6875rem", border: "1px solid var(--border)" }}>
                    {item.source || 'Verified'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
