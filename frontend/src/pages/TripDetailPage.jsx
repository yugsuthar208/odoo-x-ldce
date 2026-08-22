import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Settings, Plus, LayoutList, Map as MapIcon, Calendar, Info, Share2, Users } from "lucide-react";
import { tripService } from "../services/tripService";
import { TripMap } from "../components/map/TripMap";
import { StopDetailBar } from "../components/map/StopDetailBar";
import { StopCard } from "../components/trips/StopCard";
import { AddStopModal } from "../components/trips/AddStopModal";
import { ActivityPickerModal } from "../components/activities/ActivityPickerModal";
import TripBudget from "../components/budget/TripBudget";
import TripCollab from "../components/trips/TripCollab";
import { ActivityList } from "../components/activities/ActivityList";
import { ErrorState } from "../components/common/ErrorState";
import { PageLoader, LoadingSpinner } from "../components/common/LoadingSpinner";
import { useToast } from "../components/common/Toast";

const TABS = [
  { id: "itinerary", label: "Itinerary", icon: LayoutList },
  { id: "map", label: "Map View", icon: MapIcon },
  { id: "budget", label: "Budget", icon: Info },
  { id: "collab", label: "Team", icon: Users },
];

export default function TripDetailPage() {
  const { id } = useParams();
  const { addToast } = useToast();
  
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [activeTab, setActiveTab] = useState("itinerary");
  const [selectedStopId, setSelectedStopId] = useState(null);
  
  // Modals
  const [showAddStop, setShowAddStop] = useState(false);
  const [pickerStop, setPickerStop] = useState(null); // The stop object to add activity to

  // Data fetching
  const loadTrip = useCallback(() => {
    tripService.getTrip(id)
      .then(res => {
        const tripData = res?.data || res;
        setTrip(tripData);
        if (tripData?.stops?.length > 0) {
          setSelectedStopId(prev => (prev && tripData.stops.some(s => s.id === prev) ? prev : tripData.stops[0].id));
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { loadTrip(); }, [loadTrip]);

  // Handlers
  const handleAddStop = async (payload) => {
    await tripService.addStop(id, payload);
    addToast({ message: "Stop added to trip" });
    setShowAddStop(false);
    loadTrip();
  };

  const handleAddActivity = async (activity, targetStopId) => {
    try {
      const stopToUse = targetStopId || pickerStop?.id || selectedStop?.id;
      if (!stopToUse) throw new Error("No stop selected");
      await tripService.addItineraryItem(stopToUse, {
        activity_id: activity.id,
        scheduled_date: pickerStop?.arrival_date || selectedStop?.arrival_date || undefined
      });
      addToast({ message: "Activity added to itinerary!" });
      setPickerStop(null);
      loadTrip();
    } catch(e) {
      addToast({ message: e.message || "Failed to add activity", type: "error" });
    }
  };

  const handleRemoveActivity = async (itemId) => {
    try {
      await tripService.deleteItineraryItem(itemId);
      addToast({ message: "Activity removed" });
      loadTrip();
    } catch(e) {
      addToast({ message: e.message || "Failed to remove activity", type: "error" });
    }
  };

  if (loading) return <PageLoader />;
  if (error || !trip) return <ErrorState message={error || "Trip not found"} onRetry={loadTrip} />;

  // Derived state
  const stops = trip.stops || [];
  const selectedStop = stops.find(s => s.id === selectedStopId) || stops[0];
  const nextStop = selectedStop ? stops[stops.findIndex(s => s.id === selectedStop.id) + 1] : null;

  // Itinerary items mapped to stops
  const selectedStopActivities = selectedStop?.itinerary_items || selectedStop?.stop_activities || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Top Navigation */}
      <header style={{
        background: "var(--white)", borderBottom: "1px solid var(--border)",
        padding: "16px 32px", display: "flex", alignItems: "center", justifyContent: "space-between",
        flexShrink: 0
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Link to="/trips" className="btn btn--icon btn--ghost" style={{ marginLeft: -8 }}><ArrowLeft size={18} /></Link>
          <div>
            <h1 style={{ fontSize: "1.25rem", margin: 0 }}>{trip.title}</h1>
            <div style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--ink-soft)", fontSize: "0.8125rem", marginTop: 2 }}>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Calendar size={12} /> {trip.start_date} - {trip.end_date}</span>
              <span className={`pill pill--${trip.status}`}>{trip.status}</span>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn--ghost btn--sm"><Share2 size={14} /> Share</button>
          <button className="btn btn--icon btn--ghost"><Settings size={18} /></button>
        </div>
      </header>

      {/* Main layout */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        
        {/* Left Sidebar (Stops & Tabs) */}
        <div style={{ width: 400, background: "var(--white)", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column", flexShrink: 0 }}>
          
          {/* Tab Navigation */}
          <div style={{ display: "flex", padding: "16px 20px 0", gap: 24, borderBottom: "1px solid var(--border)" }}>
            {TABS.map(t => {
              const Icon = t.icon;
              const active = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  style={{
                    display: "flex", alignItems: "center", gap: 6,
                    padding: "0 0 12px", borderBottom: active ? "2px solid var(--ink)" : "2px solid transparent",
                    color: active ? "var(--ink)" : "var(--ink-soft)",
                    fontWeight: active ? 600 : 500, fontSize: "0.875rem"
                  }}
                >
                  <Icon size={16} /> {t.label}
                </button>
              );
            })}
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
            {activeTab === "itinerary" && (
              <>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                  <h3 style={{ fontSize: "1rem" }}>Destinations</h3>
                  <button className="btn btn--icon btn--ghost btn--sm" onClick={() => setShowAddStop(true)}><Plus size={16} /></button>
                </div>
                
                <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 32 }}>
                  {stops.length === 0 ? (
                    <div style={{ padding: 24, textAlign: "center", border: "1px dashed var(--border)", borderRadius: 12 }}>
                      <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem", marginBottom: 12 }}>No destinations yet.</p>
                      <button className="btn btn--sm btn--accent" onClick={() => setShowAddStop(true)}>Add your first stop</button>
                    </div>
                  ) : (
                    stops.map(stop => (
                      <StopCard
                        key={stop.id}
                        stop={stop}
                        isSelected={selectedStopId === stop.id}
                        onClick={() => setSelectedStopId(stop.id)}
                      />
                    ))
                  )}
                </div>

                {selectedStop && (
                  <>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                      <h3 style={{ fontSize: "1rem" }}>{selectedStop.city?.name} Activities</h3>
                      <button className="btn btn--icon btn--ghost btn--sm" onClick={() => setPickerStop(selectedStop)}><Plus size={16} /></button>
                    </div>
                    <ActivityList items={selectedStopActivities} onRemove={handleRemoveActivity} />
                  </>
                )}
              </>
            )}

            {activeTab === "budget" && <TripBudget tripId={trip.id} />}
            {activeTab === "collab" && <TripCollab tripId={trip.id} visibility={trip.visibility} />}
            {activeTab === "map" && <div className="hide-desktop">Map view takes full screen on mobile.</div>}
          </div>
        </div>

        {/* Right Map Pane */}
        <div style={{ flex: 1, position: "relative", background: "var(--surface)" }} className="hide-mobile">
          <TripMap stops={stops} selectedStopId={selectedStopId} onStopClick={(s) => setSelectedStopId(s.id)} />
          {activeTab === "itinerary" && (
            <StopDetailBar
              selectedStop={selectedStop}
              nextStop={nextStop}
              onAddActivity={() => setPickerStop(selectedStop)}
            />
          )}
        </div>
      </div>

      {/* Modals */}
      {showAddStop && <AddStopModal onClose={() => setShowAddStop(false)} onAdd={handleAddStop} />}
      {pickerStop && <ActivityPickerModal tripId={trip.id} stopId={pickerStop.id} cityId={pickerStop.city.id} onClose={() => setPickerStop(null)} onAdded={handleAddActivity} />}
      
      <style>{`@media (max-width: 768px) { .hide-mobile { display: none !important; } }`}</style>
    </div>
  );
}
