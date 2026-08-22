import React, { useState } from 'react';
import { tripService } from '../../services/tripService';
import { useToast } from '../common/Toast';
import { Train, Plane, Bus, Car, Clock, Compass, ArrowRight, CheckCircle2, Navigation } from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

export default function TransitOptimizer({ trip, onRefresh }) {
  const { addToast } = useToast();
  const [selectedMode, setSelectedMode] = useState('all');
  const [loadingLeg, setLoadingLeg] = useState(null);

  const getModeDetails = (mode) => {
    switch (mode?.toLowerCase()) {
      case 'train': 
        return { icon: Train, label: 'Train', color: '#f59e0b', bg: '#fef3c7' };
      case 'flight': 
        return { icon: Plane, label: 'Flight', color: '#3b82f6', bg: '#dbeafe' };
      case 'bus': 
        return { icon: Bus, label: 'Bus', color: '#10b981', bg: '#d1fae5' };
      case 'cab': 
        return { icon: Car, label: 'Cab', color: '#8b5cf6', bg: '#ede9fe' };
      default: 
        return { icon: Compass, label: 'Transit', color: 'var(--ink-soft)', bg: 'var(--surface)' };
    }
  };

  const handleSelectOption = async (legId, optionId) => {
    setLoadingLeg(legId);
    try {
      await tripService.selectTransitOption(trip.id, legId, optionId);
      addToast({ message: "Transit option selected & budget recalculated!" });
      if (onRefresh) onRefresh();
    } catch (err) {
      addToast({ message: err.message || "Failed to select option", type: "error" });
    } finally {
      setLoadingLeg(null);
    }
  };

  if (!trip?.transit_legs || trip.transit_legs.length === 0) {
    return (
      <div className="card fade-in" style={{ padding: "48px 24px", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
        <div style={{ width: 56, height: 56, borderRadius: "50%", background: "var(--surface)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Navigation size={28} color="var(--ink-soft)" />
        </div>
        <div>
          <h3 style={{ fontSize: "1.1rem", marginBottom: 6 }}>No transit legs generated yet</h3>
          <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem", maxWidth: 320, margin: "0 auto" }}>
            Add stops to your trip itinerary to automatically generate multi-modal travel options with real pricing.
          </p>
        </div>
      </div>
    );
  }

  // Helper to find city names
  const getCityName = (stopId) => {
    if (!stopId) return trip.origin_city || "Origin City";
    const stop = trip.stops?.find(s => s.id === stopId);
    return stop?.city?.name || stop?.city_name || "Destination";
  };

  const modes = [
    { id: 'all', label: 'All Modes' },
    { id: 'train', label: 'Trains' },
    { id: 'flight', label: 'Flights' },
    { id: 'bus', label: 'Buses' },
    { id: 'cab', label: 'Cabs' },
  ];

  return (
    <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", border: "1px solid rgba(195, 248, 50, 0.5)" }}>
            ⚡ Smart Route Engine
          </span>
        </div>
        <h2 style={{ fontSize: "1.35rem", fontWeight: 700, margin: "6px 0 4px" }}>Multi-Modal Travel</h2>
        <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
          Select the best transport options for each leg of your journey to automatically update total trip budget.
        </p>
      </div>

      {/* Mode Filters */}
      <div style={{
        display: "flex",
        gap: 6,
        background: "var(--surface)",
        padding: 4,
        borderRadius: "var(--radius-pill)",
        border: "1px solid var(--border)",
        overflowX: "auto",
        width: "fit-content"
      }}>
        {modes.map((m) => {
          const active = selectedMode === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setSelectedMode(m.id)}
              style={{
                padding: "6px 14px",
                borderRadius: "var(--radius-pill)",
                fontSize: "0.8125rem",
                fontWeight: active ? 700 : 500,
                background: active ? "var(--ink)" : "transparent",
                color: active ? "var(--accent)" : "var(--ink-soft)",
                transition: "all var(--t-fast)",
                whiteSpace: "nowrap",
                cursor: "pointer"
              }}
            >
              {m.label}
            </button>
          );
        })}
      </div>

      {/* Transit Legs */}
      <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
        {trip.transit_legs.map((leg, legIdx) => {
          const fromName = getCityName(leg.from_stop_id);
          const toName = getCityName(leg.to_stop_id);
          const filteredOptions = (leg.options || []).filter(
            opt => selectedMode === 'all' || opt.mode === selectedMode
          );

          return (
            <div key={leg.id} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {/* Leg Route Badge */}
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "12px 18px",
                background: "var(--surface)",
                borderRadius: "var(--radius-input)",
                border: "1px solid var(--border)"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: "0.9375rem" }}>
                  <span style={{ fontWeight: 700, color: "var(--ink)" }}>{fromName}</span>
                  <ArrowRight size={16} color="var(--ink-soft)" />
                  <span style={{ fontWeight: 700, color: "var(--ink)" }}>{toName}</span>
                </div>
                <span className="pill" style={{ background: "var(--white)", border: "1px solid var(--border)", color: "var(--ink-soft)", fontSize: "0.75rem" }}>
                  Leg {legIdx + 1}
                </span>
              </div>

              {/* Options Grid */}
              {filteredOptions.length === 0 ? (
                <div className="card" style={{ padding: 24, textAlign: "center", background: "var(--surface)" }}>
                  <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
                    No {selectedMode} options available for this leg distance. Try switching modes.
                  </p>
                </div>
              ) : (
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                  gap: 14
                }}>
                  {filteredOptions.map((opt) => {
                    const isSelected = leg.selected_option_id === opt.id;
                    const { icon: ModeIcon, color: iconColor, bg: iconBg } = getModeDetails(opt.mode);

                    return (
                      <div
                        key={opt.id}
                        className="card"
                        style={{
                          padding: 16,
                          display: "flex",
                          flexDirection: "column",
                          justifyContent: "space-between",
                          border: isSelected ? "2px solid var(--ink)" : "1px solid var(--border)",
                          background: isSelected ? "var(--white)" : "var(--white)",
                          boxShadow: isSelected ? "var(--shadow-float)" : "var(--shadow-card)",
                          borderRadius: "var(--radius-card)",
                          position: "relative",
                          transition: "all var(--t-fast)"
                        }}
                      >
                        {isSelected && (
                          <div style={{
                            position: "absolute",
                            top: -9,
                            right: 12,
                            background: "var(--ink)",
                            color: "var(--accent)",
                            fontSize: "0.6875rem",
                            fontWeight: 700,
                            padding: "2px 8px",
                            borderRadius: "var(--radius-pill)",
                            display: "flex",
                            alignItems: "center",
                            gap: 4
                          }}>
                            <CheckCircle2 size={12} /> Active Choice
                          </div>
                        )}

                        <div>
                          {/* Header: Mode Icon + Provider */}
                          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                            <div style={{
                              width: 38,
                              height: 38,
                              borderRadius: "var(--radius-input)",
                              background: iconBg,
                              color: iconColor,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexShrink: 0
                            }}>
                              <ModeIcon size={20} />
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <h4 style={{ margin: 0, fontSize: "0.9375rem", fontWeight: 700, color: "var(--ink)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                                {opt.provider}
                              </h4>
                              <div style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--ink-soft)", fontSize: "0.75rem", marginTop: 2 }}>
                                <Clock size={12} />
                                <span>~{opt.duration_hours}h duration</span>
                              </div>
                            </div>
                          </div>

                          {/* Pricing Box */}
                          <div style={{
                            background: "var(--surface)",
                            padding: "10px 12px",
                            borderRadius: "var(--radius-input)",
                            marginBottom: 14,
                            display: "flex",
                            alignItems: "baseline",
                            justifyContent: "space-between"
                          }}>
                            <div>
                              <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--ink)" }}>
                                ₹{Number(opt.cost_per_person || 0).toLocaleString('en-IN')}
                              </span>
                              <span style={{ fontSize: "0.75rem", color: "var(--ink-soft)", marginLeft: 4 }}>
                                / person
                              </span>
                            </div>
                            <span style={{ fontSize: "0.75rem", color: "var(--ink-soft)", fontWeight: 500 }}>
                              Total: ₹{Number(opt.total_estimated_cost || 0).toLocaleString('en-IN')}
                            </span>
                          </div>
                        </div>

                        {/* Action Button */}
                        <button
                          disabled={loadingLeg === leg.id}
                          onClick={() => handleSelectOption(leg.id, opt.id)}
                          className={`btn btn--sm ${isSelected ? 'btn--primary' : 'btn--secondary'}`}
                          style={{
                            width: "100%",
                            justifyContent: "center",
                            fontWeight: 700,
                            borderRadius: "var(--radius-input)",
                            background: isSelected ? "var(--ink)" : undefined,
                            color: isSelected ? "var(--accent)" : undefined
                          }}
                        >
                          {loadingLeg === leg.id ? (
                            <LoadingSpinner size={14} color={isSelected ? "var(--accent)" : "var(--ink)"} />
                          ) : isSelected ? (
                            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                              <CheckCircle2 size={14} /> Selected
                            </span>
                          ) : (
                            "Select Option"
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
