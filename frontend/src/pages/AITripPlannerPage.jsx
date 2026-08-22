import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Sparkles, 
  MapPin, 
  Calendar, 
  Users, 
  Train, 
  Plane, 
  Car, 
  Utensils, 
  Compass, 
  Clock, 
  CheckCircle2, 
  ArrowRight, 
  DollarSign, 
  Bookmark, 
  Coffee, 
  Landmark, 
  Sunset, 
  Moon, 
  ShieldCheck, 
  Star,
  Hotel,
  Share2
} from "lucide-react";
import { aiPlannerService } from "../services/aiPlannerService";
import { TripMap } from "../components/map/TripMap";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { useToast } from "../components/common/Toast";

const PRESET_TRIPS = [
  {
    title: "Royal Gujarat Circuit",
    origin: "Mumbai",
    dest: "Ahmedabad, Gandhinagar, Statue of Unity (Kevadia)",
    days: 4,
    budget: "mid",
    style: "cultural",
    transit: "train",
    diet: "authentic_regional",
    interests: ["heritage", "food", "sightseeing", "monuments"]
  },
  {
    title: "Rajasthan Heritage Tour",
    origin: "Delhi",
    dest: "Jaipur, Jodhpur, Udaipur",
    days: 6,
    budget: "mid",
    style: "cultural",
    transit: "train",
    diet: "authentic_regional",
    interests: ["heritage", "food", "sightseeing", "shopping"]
  },
  {
    title: "Kerala Backwaters & Mist",
    origin: "Mumbai",
    dest: "Munnar, Alleppey (Alappuzha), Kochi",
    days: 5,
    budget: "luxury",
    style: "romantic",
    transit: "flight",
    diet: "all",
    interests: ["nature", "food", "relaxation", "scenic"]
  },
  {
    title: "Tokyo & Kyoto Explorer",
    origin: "Tokyo",
    dest: "Tokyo, Kyoto",
    days: 6,
    budget: "luxury",
    style: "explorer",
    transit: "train",
    diet: "authentic_regional",
    interests: ["technology", "food", "heritage", "shopping"]
  }
];

const INTEREST_OPTIONS = [
  { id: "heritage", label: "🏰 Heritage & Palaces" },
  { id: "food", label: "🍲 Iconic Food & Thalis" },
  { id: "nature", label: "🏔️ Nature & Landscapes" },
  { id: "shopping", label: "🛍️ Bazaars & Crafts" },
  { id: "sunset", label: "🌅 Sunset & Viewpoints" },
  { id: "nightlife", label: "✨ Nightlife & Cafes" },
  { id: "spiritual", label: "🛕 Spiritual & Temples" }
];

export default function AITripPlannerPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  // Form State
  const [originCity, setOriginCity] = useState("Mumbai");
  const [destInput, setDestInput] = useState("Gandhinagar, Udaipur");
  const [durationDays, setDurationDays] = useState(4);
  const [travelers, setTravelers] = useState(2);
  const [budgetTier, setBudgetTier] = useState("mid");
  const [travelStyle, setTravelStyle] = useState("explorer");
  const [transitPref, setTransitPref] = useState("train");
  const [dietaryPref, setDietaryPref] = useState("authentic_regional");
  const [selectedInterests, setSelectedInterests] = useState(["heritage", "food", "nature", "sightseeing"]);
  const [startDate, setStartDate] = useState(new Date(Date.now() + 14 * 86400000).toISOString().split("T")[0]);

  // Output State
  const [generating, setGenerating] = useState(false);
  const [blueprint, setBlueprint] = useState(null);
  const [savingTrip, setSavingTrip] = useState(false);
  const [activeDayTab, setActiveDayTab] = useState(1);

  const toggleInterest = (id) => {
    setSelectedInterests(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const applyPreset = (preset) => {
    setOriginCity(preset.origin);
    setDestInput(preset.dest);
    setDurationDays(preset.days);
    setBudgetTier(preset.budget);
    setTravelStyle(preset.style);
    setTransitPref(preset.transit);
    setDietaryPref(preset.diet);
    setSelectedInterests(preset.interests);
  };

  const handleGenerate = async (e) => {
    if (e) e.preventDefault();
    if (!destInput.trim()) {
      addToast({ message: "Please enter at least one destination city", type: "error" });
      return;
    }

    setGenerating(true);
    setBlueprint(null);

    try {
      const res = await aiPlannerService.generateItinerary({
        origin_city: originCity.trim(),
        destination_input: destInput.trim(),
        duration_days: parseInt(durationDays),
        travelers: parseInt(travelers),
        budget_tier: budgetTier,
        travel_style: travelStyle,
        transit_preference: transitPref,
        dietary_preference: dietaryPref,
        interests: selectedInterests,
        start_date: startDate,
      });

      if (res?.success && res.data) {
        setBlueprint(res.data);
        setActiveDayTab(1);
        addToast({ message: "Master AI Trip Blueprint generated successfully!" });
        // Scroll down to results
        setTimeout(() => {
          document.getElementById("ai-blueprint-section")?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } else {
        throw new Error(res?.error || "Failed to generate itinerary");
      }
    } catch (err) {
      console.error(err);
      addToast({ message: err.message || "AI Planner failed to generate blueprint", type: "error" });
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveToDatabase = async () => {
    if (!blueprint) return;
    setSavingTrip(true);
    try {
      const res = await aiPlannerService.saveTrip(blueprint);
      if (res?.success && res.data?.trip_id) {
        addToast({ message: "Trip saved to My Trips! Redirecting..." });
        setTimeout(() => {
          navigate(`/trips/${res.data.trip_id}`);
        }, 800);
      } else {
        throw new Error(res?.error || "Failed to save trip");
      }
    } catch (err) {
      console.error(err);
      addToast({ message: err.message || "Failed to save trip to database", type: "error" });
    } finally {
      setSavingTrip(false);
    }
  };

  // Convert blueprint map_stops for TripMap
  const mapStops = (blueprint?.map_stops || []).map((s, idx) => ({
    id: s.id || `stop_${idx}`,
    stop_order: idx,
    city_name: s.city_name,
    city: {
      name: s.city_name,
      country: s.country,
      latitude: s.latitude,
      longitude: s.longitude,
      image_url: s.image_url,
    },
    arrival_date: blueprint.start_date,
    departure_date: blueprint.end_date,
  }));

  const mapTripObj = blueprint ? {
    transit_mode: blueprint.transit_legs?.[0]?.mode || transitPref,
    transit_legs: (blueprint.transit_legs || []).map((leg, idx) => ({
      id: `leg_${idx}`,
      from_stop_id: `stop_${idx}`,
      to_stop_id: `stop_${idx + 1}`,
      selected_option_id: `opt_${idx}`,
      selected_option: { mode: leg.mode },
      options: [{ id: `opt_${idx}`, mode: leg.mode }]
    }))
  } : null;

  return (
    <div className="page fade-in" style={{ maxWidth: 1180, margin: "0 auto", paddingBottom: 80 }}>
      {/* Header Banner */}
      <div style={{ marginBottom: 32, textAlign: "left" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", border: "1px solid rgba(195, 248, 50, 0.5)", fontWeight: 700 }}>
            <Sparkles size={13} /> Tripora AI Master Brain
          </span>
        </div>
        <h1 style={{ fontSize: "2.25rem", fontWeight: 800, letterSpacing: "-0.03em", margin: "0 0 8px" }}>
          AI Trip Planner
        </h1>
        <p style={{ color: "var(--ink-soft)", fontSize: "1rem", maxWidth: 680 }}>
          Tell the AI where you want to travel. In seconds, it designs a complete, hour-by-hour scheduled itinerary with live route mapping, must-eat regional food spots, transit recommendations, and full budget forecasts.
        </p>
      </div>

      {/* Quick Inspiration Presets */}
      <div style={{ marginBottom: 28 }}>
        <span style={{ fontSize: "0.8125rem", fontWeight: 700, color: "var(--ink-soft)", textTransform: "uppercase", letterSpacing: "0.5px", display: "block", marginBottom: 10 }}>
          ⚡ Fast Inspiration Presets
        </span>
        <div style={{ display: "flex", gap: 10, overflowX: "auto", paddingBottom: 4 }}>
          {PRESET_TRIPS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => applyPreset(preset)}
              className="card card--hover"
              style={{
                padding: "10px 16px",
                borderRadius: "var(--radius-pill)",
                fontSize: "0.85rem",
                fontWeight: 600,
                whiteSpace: "nowrap",
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: "var(--white)",
                border: "1px solid var(--border)",
                cursor: "pointer"
              }}
            >
              <span>{preset.title}</span>
              <span className="pill" style={{ background: "var(--surface)", fontSize: "0.75rem", padding: "2px 8px" }}>
                {preset.days} Days
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Console Form */}
      <form onSubmit={handleGenerate} className="card" style={{ padding: 32, borderRadius: "var(--radius-card)", marginBottom: 40, border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}>
        <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
          <Compass size={20} color="var(--ink)" /> Configure Trip Parameters
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20, marginBottom: 24 }}>
          {/* Origin */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <MapPin size={14} /> Starting / Origin City
            </label>
            <input
              type="text"
              className="input"
              value={originCity}
              onChange={(e) => setOriginCity(e.target.value)}
              placeholder="e.g. Mumbai, Delhi, Tokyo..."
              required
            />
          </div>

          {/* Destinations */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Compass size={14} /> Destination City / Circuit
            </label>
            <input
              type="text"
              className="input"
              value={destInput}
              onChange={(e) => setDestInput(e.target.value)}
              placeholder="e.g. Gandhinagar, Udaipur, Jaipur..."
              required
            />
          </div>

          {/* Duration */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Calendar size={14} /> Duration ({durationDays} Days)
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <input
                type="range"
                min="1"
                max="14"
                value={durationDays}
                onChange={(e) => setDurationDays(e.target.value)}
                style={{ flex: 1, accentColor: "var(--ink)" }}
              />
              <span style={{ fontWeight: 800, width: 40, textAlign: "right" }}>{durationDays}d</span>
            </div>
          </div>

          {/* Travelers */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Users size={14} /> Group Size ({travelers} Travelers)
            </label>
            <div style={{ display: "flex", gap: 6 }}>
              {[1, 2, 4, 6, 8].map(num => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setTravelers(num)}
                  style={{
                    flex: 1,
                    padding: "8px 0",
                    borderRadius: "var(--radius-input)",
                    fontSize: "0.85rem",
                    fontWeight: travelers === num ? 800 : 500,
                    background: travelers === num ? "var(--ink)" : "var(--surface)",
                    color: travelers === num ? "var(--accent)" : "var(--ink)",
                    border: "1px solid var(--border)",
                    cursor: "pointer",
                    transition: "all var(--t-fast)"
                  }}
                >
                  {num === 1 ? "Solo" : num === 2 ? "Couple" : `${num}`}
                </button>
              ))}
            </div>
          </div>

          {/* Budget Tier */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <DollarSign size={14} /> Budget Tier
            </label>
            <div style={{ display: "flex", gap: 6 }}>
              {[
                { id: "budget", label: "Budget" },
                { id: "mid", label: "Mid-Range" },
                { id: "luxury", label: "Luxury" }
              ].map(tier => (
                <button
                  key={tier.id}
                  type="button"
                  onClick={() => setBudgetTier(tier.id)}
                  style={{
                    flex: 1,
                    padding: "8px 0",
                    borderRadius: "var(--radius-input)",
                    fontSize: "0.85rem",
                    fontWeight: budgetTier === tier.id ? 800 : 500,
                    background: budgetTier === tier.id ? "var(--ink)" : "var(--surface)",
                    color: budgetTier === tier.id ? "var(--accent)" : "var(--ink)",
                    border: "1px solid var(--border)",
                    cursor: "pointer",
                    transition: "all var(--t-fast)"
                  }}
                >
                  {tier.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preferred Transit Mode */}
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Train size={14} /> Primary Transit Mode
            </label>
            <select
              className="input"
              value={transitPref}
              onChange={(e) => setTransitPref(e.target.value)}
            >
              <option value="train">🚆 Vande Bharat / Superfast Trains</option>
              <option value="flight">✈️ Domestic / International Flights</option>
              <option value="cab">🚗 Private Intercity AC Cab / Road</option>
              <option value="bus">🚌 Luxury Volvo Sleeper Bus</option>
              <option value="optimal">⚡ Smart AI Auto-Optimal</option>
            </select>
          </div>
        </div>

        {/* Interest Tags */}
        <div style={{ marginBottom: 28 }}>
          <label className="label" style={{ marginBottom: 10 }}>Select Travel Vibes & Passions</label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {INTEREST_OPTIONS.map(opt => {
              const active = selectedInterests.includes(opt.id);
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => toggleInterest(opt.id)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "var(--radius-pill)",
                    fontSize: "0.8125rem",
                    fontWeight: active ? 700 : 500,
                    background: active ? "var(--ink)" : "var(--surface)",
                    color: active ? "var(--accent)" : "var(--ink-soft)",
                    border: active ? "1px solid var(--ink)" : "1px solid var(--border)",
                    cursor: "pointer",
                    transition: "all var(--t-fast)"
                  }}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Generate Button */}
        <button
          type="submit"
          disabled={generating}
          className="btn btn--primary"
          style={{
            width: "100%",
            padding: "16px 24px",
            fontSize: "1.05rem",
            fontWeight: 800,
            borderRadius: "var(--radius-input)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
            background: "var(--ink)",
            color: "var(--accent)",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.15)"
          }}
        >
          {generating ? (
            <>
              <LoadingSpinner size={18} color="var(--accent)" />
              <span>AI Synthesizing Master Itinerary, Maps & Food Guide...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Generate Master AI Itinerary</span>
            </>
          )}
        </button>
      </form>

      {/* ============================================================ */}
      {/* GENERATED MASTER BLUEPRINT OUTPUT SECTION */}
      {/* ============================================================ */}
      {blueprint && (
        <div id="ai-blueprint-section" className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 36 }}>
          
          {/* Master Hero Banner */}
          <div className="card" style={{
            position: "relative",
            overflow: "hidden",
            borderRadius: "var(--radius-card)",
            padding: 32,
            background: "linear-gradient(135deg, #1c1c1b 0%, #292928 100%)",
            color: "#ffffff",
            boxShadow: "var(--shadow-float)"
          }}>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between", gap: 20 }}>
              <div style={{ flex: 1, minWidth: 280 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "#c3f832", border: "1px solid rgba(195, 248, 50, 0.4)", fontWeight: 700 }}>
                    ⚡ AI Master Plan Ready
                  </span>
                </div>
                <h2 style={{ fontSize: "1.85rem", fontWeight: 800, color: "#ffffff", margin: "4px 0 8px" }}>
                  {blueprint.trip_title}
                </h2>
                <p style={{ color: "#a1a1aa", fontSize: "0.9375rem", maxWidth: 620 }}>
                  {blueprint.tagline} • From {blueprint.start_date} to {blueprint.end_date}
                </p>

                {/* Key Metric Badges */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 20 }}>
                  <div style={{ background: "rgba(255, 255, 255, 0.08)", padding: "8px 14px", borderRadius: "var(--radius-input)", border: "1px solid rgba(255, 255, 255, 0.12)" }}>
                    <span style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block" }}>Total Estimated Budget</span>
                    <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "#c3f832" }}>
                      ₹{Number(blueprint.budget_summary?.total_estimated_cost || 0).toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div style={{ background: "rgba(255, 255, 255, 0.08)", padding: "8px 14px", borderRadius: "var(--radius-input)", border: "1px solid rgba(255, 255, 255, 0.12)" }}>
                    <span style={{ fontSize: "0.75rem", color: "#a1a1aa", display: "block" }}>Cost Per Person</span>
                    <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "#ffffff" }}>
                      ₹{Number(blueprint.budget_summary?.cost_per_person || 0).toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              </div>

              {/* 1-Click Save Action */}
              <div style={{ alignSelf: "center" }}>
                <button
                  onClick={handleSaveToDatabase}
                  disabled={savingTrip}
                  className="btn btn--primary"
                  style={{
                    padding: "14px 24px",
                    fontWeight: 800,
                    fontSize: "0.95rem",
                    borderRadius: "var(--radius-pill)",
                    background: "#c3f832",
                    color: "#191919",
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    boxShadow: "0 4px 16px rgba(195, 248, 50, 0.4)",
                    cursor: "pointer"
                  }}
                >
                  {savingTrip ? (
                    <LoadingSpinner size={16} color="#191919" />
                  ) : (
                    <>
                      <Bookmark size={16} />
                      <span>Save & Open in My Trips</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Interactive Live Map Section */}
          <div className="card" style={{ padding: 24, borderRadius: "var(--radius-card)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <div>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, margin: 0 }}>
                  🗺️ Live Interactive Route & Destination Points
                </h3>
                <p style={{ color: "var(--ink-soft)", fontSize: "0.85rem", marginTop: 2 }}>
                  Exact coordinates with mode-aware turn-by-turn routing vectors.
                </p>
              </div>
            </div>
            <div style={{ height: 380, borderRadius: "var(--radius-card)", overflow: "hidden", border: "1px solid var(--border)" }}>
              <TripMap stops={mapStops} trip={mapTripObj} />
            </div>
          </div>

          {/* Hour-by-Hour Scheduled Timeline */}
          <div className="card" style={{ padding: 28, borderRadius: "var(--radius-card)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, flexWrap: "wrap", gap: 12 }}>
              <div>
                <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: 0 }}>
                  📅 Hour-by-Hour Master Schedule (X Time to Y Time)
                </h3>
                <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem", marginTop: 2 }}>
                  Time-blocked daily plan with sightseeing, food crawls, travel buffers, and evening dining.
                </p>
              </div>

              {/* Day Selector Pills */}
              <div style={{ display: "flex", gap: 6, overflowX: "auto", padding: 4, background: "var(--surface)", borderRadius: "var(--radius-pill)", border: "1px solid var(--border)" }}>
                {(blueprint.itinerary_days || []).map((day) => (
                  <button
                    key={day.day_number}
                    onClick={() => setActiveDayTab(day.day_number)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: "var(--radius-pill)",
                      fontSize: "0.8125rem",
                      fontWeight: activeDayTab === day.day_number ? 800 : 500,
                      background: activeDayTab === day.day_number ? "var(--ink)" : "transparent",
                      color: activeDayTab === day.day_number ? "var(--accent)" : "var(--ink-soft)",
                      cursor: "pointer",
                      transition: "all var(--t-fast)"
                    }}
                  >
                    Day {day.day_number}
                  </button>
                ))}
              </div>
            </div>

            {/* Active Day Schedule Content */}
            {(() => {
              const activeDay = (blueprint.itinerary_days || []).find(d => d.day_number === activeDayTab) || blueprint.itinerary_days?.[0];
              if (!activeDay) return null;

              return (
                <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div style={{ padding: "12px 16px", background: "var(--surface)", borderRadius: "var(--radius-input)", border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>{activeDay.theme}</span>
                    <span className="pill" style={{ background: "var(--white)", border: "1px solid var(--border)" }}>
                      Estimated Day Cost: ₹{Number(activeDay.day_total_cost_inr || 0).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    {(activeDay.schedule || []).map((item, sIdx) => (
                      <div
                        key={sIdx}
                        className="card card--hover"
                        style={{
                          padding: 16,
                          borderRadius: "var(--radius-input)",
                          display: "flex",
                          gap: 16,
                          alignItems: "flex-start",
                          border: "1px solid var(--border)",
                          background: "var(--white)"
                        }}
                      >
                        {/* Time Slot Badge */}
                        <div style={{
                          background: "var(--surface)",
                          padding: "8px 12px",
                          borderRadius: "var(--radius-input)",
                          textAlign: "center",
                          minWidth: 110,
                          flexShrink: 0,
                          border: "1px solid var(--border)"
                        }}>
                          <div style={{ fontSize: "0.75rem", color: "var(--ink-soft)", fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
                            <Clock size={12} /> {item.time_slot}
                          </div>
                          <span style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--ink)", textTransform: "uppercase", marginTop: 2, display: "block" }}>
                            {item.slot_name}
                          </span>
                        </div>

                        {/* Activity Details */}
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 4 }}>
                            <h4 style={{ margin: 0, fontSize: "1rem", fontWeight: 700, color: "var(--ink)" }}>
                              {item.title}
                            </h4>
                            <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", fontSize: "0.75rem", fontWeight: 700 }}>
                              ₹{Number(item.estimated_cost_inr || 0).toLocaleString('en-IN')}
                            </span>
                          </div>

                          <p style={{ fontSize: "0.85rem", color: "var(--ink-soft)", lineHeight: 1.5, margin: "4px 0 8px" }}>
                            {item.description}
                          </p>

                          <div style={{ fontSize: "0.75rem", color: "#b45309", background: "#fef3c7", padding: "4px 10px", borderRadius: "var(--radius-pill)", display: "inline-flex", alignItems: "center", gap: 6, fontWeight: 600 }}>
                            <span>💡 Insider Tip:</span>
                            <span>{item.insider_tip}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}
          </div>

          {/* "Must-Eat" Regional Culinary Guide */}
          <div className="card" style={{ padding: 28, borderRadius: "var(--radius-card)" }}>
            <div style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                <span className="pill" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#b45309", border: "1px solid rgba(245, 158, 11, 0.3)", fontWeight: 700 }}>
                  🍲 Regional Gastronomy
                </span>
              </div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "4px 0" }}>
                Must-Eat Delicacies & Iconic Food Spots
              </h3>
              <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>
                Legendary regional thalis, iconic dhabas, street food alleys, and traditional sweets curated by food experts.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
              {(blueprint.culinary_guides || []).map((guide, gIdx) => (
                <div key={gIdx} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <h4 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--ink)", display: "flex", alignItems: "center", gap: 6 }}>
                    <MapPin size={16} color="var(--accent)" /> {guide.city_name} Specialties
                  </h4>

                  {guide.delicacies.map((food, fIdx) => (
                    <div
                      key={fIdx}
                      className="card card--hover"
                      style={{
                        padding: 16,
                        borderRadius: "var(--radius-card)",
                        border: "1px solid var(--border)",
                        background: "var(--white)",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between"
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                          <span className="pill" style={{ background: "rgba(195, 248, 50, 0.2)", color: "var(--ink)", fontSize: "0.6875rem", fontWeight: 700 }}>
                            {food.type}
                          </span>
                          <span style={{ fontSize: "0.8125rem", fontWeight: 700, color: "var(--ink)" }}>
                            {food.cost_inr}
                          </span>
                        </div>

                        <h5 style={{ fontSize: "0.95rem", fontWeight: 700, margin: "0 0 6px", color: "var(--ink)" }}>
                          {food.name}
                        </h5>

                        <p style={{ fontSize: "0.8125rem", color: "var(--ink-soft)", lineHeight: 1.5, marginBottom: 10 }}>
                          {food.highlight}
                        </p>
                      </div>

                      <div style={{ borderTop: "1px solid var(--border)", paddingTop: 8, fontSize: "0.75rem", color: "var(--ink-soft)", display: "flex", alignItems: "center", gap: 4 }}>
                        <span style={{ fontWeight: 600, color: "var(--ink)" }}>Iconic Spot:</span>
                        <span>{food.famous_spot}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Transit & Stay Recommendations */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
            {/* Transit Legs */}
            <div className="card" style={{ padding: 24, borderRadius: "var(--radius-card)" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
                <Train size={18} /> Recommended Inter-City Transit
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {(blueprint.transit_legs || []).map((leg, idx) => (
                  <div key={idx} style={{ padding: 14, background: "var(--surface)", borderRadius: "var(--radius-input)", border: "1px solid var(--border)" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>
                        {leg.from_city} → {leg.to_city}
                      </span>
                      <span className="pill" style={{ background: "var(--white)", border: "1px solid var(--border)", fontWeight: 700 }}>
                        Leg {leg.leg_number}
                      </span>
                    </div>
                    <p style={{ fontSize: "0.8125rem", color: "var(--ink)", fontWeight: 600, margin: 0 }}>
                      {leg.provider} (~{leg.duration_hours}h)
                    </p>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--ink-soft)", marginTop: 6 }}>
                      <span>₹{Number(leg.cost_per_person_inr || 0).toLocaleString('en-IN')} / person</span>
                      <span style={{ fontWeight: 700, color: "var(--ink)" }}>Total: ₹{Number(leg.total_cost_inr || 0).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Budget Breakdown */}
            <div className="card" style={{ padding: 24, borderRadius: "var(--radius-card)" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
                <DollarSign size={18} /> Master Budget Breakdown (₹ INR)
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>Accommodations / Stays</span>
                  <span style={{ fontWeight: 700 }}>₹{Number(blueprint.budget_summary?.breakdown?.stays || 0).toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>Multi-Modal Transportation</span>
                  <span style={{ fontWeight: 700 }}>₹{Number(blueprint.budget_summary?.breakdown?.transport || 0).toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>Activities & Sightseeing</span>
                  <span style={{ fontWeight: 700 }}>₹{Number(blueprint.budget_summary?.breakdown?.activities || 0).toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>Food & Dining Allowance</span>
                  <span style={{ fontWeight: 700 }}>₹{Number(blueprint.budget_summary?.breakdown?.food || 0).toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 0 0", fontSize: "1.1rem", fontWeight: 800 }}>
                  <span>Total Estimated Cost</span>
                  <span style={{ color: "var(--ink)" }}>₹{Number(blueprint.budget_summary?.total_estimated_cost || 0).toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Call to Action */}
          <div className="card" style={{ padding: 32, textAlign: "center", background: "var(--surface)", border: "1px dashed var(--border)", borderRadius: "var(--radius-card)" }}>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>
              Ready to embark on this journey?
            </h3>
            <p style={{ color: "var(--ink-soft)", fontSize: "0.9375rem", marginBottom: 20 }}>
              Save this blueprint into your active workspace to edit stops, invite collaborators, adjust expenses, and track real-time budgets.
            </p>
            <button
              onClick={handleSaveToDatabase}
              disabled={savingTrip}
              className="btn btn--primary"
              style={{
                padding: "14px 28px",
                fontWeight: 800,
                fontSize: "1rem",
                borderRadius: "var(--radius-pill)",
                background: "var(--ink)",
                color: "var(--accent)"
              }}
            >
              {savingTrip ? <LoadingSpinner size={16} color="var(--accent)" /> : "Save & Open in My Trips"}
            </button>
          </div>

        </div>
      )}
    </div>
  );
}
