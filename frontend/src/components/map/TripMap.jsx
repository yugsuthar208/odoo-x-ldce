import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapPin, Navigation, Plane, Train, Car, Bus } from "lucide-react";
import { getLegRouteGeometry } from "../../services/routeService";

// Fix default leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:       "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:     "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

/**
 * Creates a unified, luxury dark-themed pinpoint marker.
 * Anchored precisely at the bottom tip [18, 44] for exact coordinate accuracy.
 */
function createUnifiedCityMarker(label, orderNumber, isSelected) {
  const accentColor = "#c3f832";
  const darkColor = "#191919";

  const html = `
    <div style="
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transform: translate3d(0, 0, 0);
    ">
      <!-- Pin Marker Bubble -->
      <div style="
        width: 36px;
        height: 36px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        background: ${isSelected ? accentColor : darkColor};
        border: 2.5px solid ${isSelected ? darkColor : accentColor};
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
      ">
        <span style="
          transform: rotate(45deg);
          font-family: 'DM Sans', sans-serif;
          font-weight: 800;
          font-size: 13px;
          color: ${isSelected ? darkColor : "#ffffff"};
        ">${orderNumber}</span>
      </div>

      <!-- City Label Pill -->
      <div style="
        margin-top: 6px;
        background: rgba(25, 25, 25, 0.92);
        backdrop-filter: blur(6px);
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 999px;
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
        border: 1px solid rgba(195, 248, 50, 0.35);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
      ">${label}</div>
    </div>
  `;

  return L.divIcon({
    className: "custom-city-marker",
    html: html,
    iconSize: [36, 60],
    iconAnchor: [18, 36], // Point marker tip precisely at coordinate center
    popupAnchor: [0, -36],
  });
}

function FitBounds({ coords }) {
  const map = useMap();
  useEffect(() => {
    if (coords.length >= 2) {
      map.fitBounds(coords, { padding: [60, 60], maxZoom: 12 });
    } else if (coords.length === 1) {
      map.setView(coords[0], 9);
    }
  }, [coords, map]);
  return null;
}

export function TripMap({ stops = [], selectedStopId = null, onStopClick, trip = null }) {
  const [legRoutes, setLegRoutes] = useState([]);
  const [loadingRoutes, setLoadingRoutes] = useState(false);

  const validStops = stops
    .filter((s) => s.city?.latitude && s.city?.longitude)
    .sort((a, b) => (a.stop_order ?? 0) - (b.stop_order ?? 0));

  const coords = validStops.map((s) => [s.city.latitude, s.city.longitude]);
  const center = coords.length > 0 ? coords[0] : [20, 77];

  // Helper to determine the transit mode for a given leg between stopA and stopB
  const getLegMode = (stopA, stopB) => {
    if (!trip?.transit_legs) return trip?.transit_mode || "road";

    // Find matching leg in trip.transit_legs
    const leg = trip.transit_legs.find(
      (l) => l.from_stop_id === stopA.id && l.to_stop_id === stopB.id
    ) || trip.transit_legs.find(
      (l) => l.to_stop_id === stopB.id
    );

    if (leg) {
      if (leg.selected_option?.mode) return leg.selected_option.mode;
      if (leg.selected_option_id && leg.options) {
        const opt = leg.options.find((o) => o.id === leg.selected_option_id);
        if (opt?.mode) return opt.mode;
      }
      if (leg.options && leg.options.length > 0) {
        return leg.options[0].mode;
      }
    }

    return trip?.transit_mode || "road";
  };

  // Async Multi-Modal Route Calculation
  useEffect(() => {
    let isMounted = true;

    async function computeRoutes() {
      if (validStops.length < 2) {
        setLegRoutes([]);
        return;
      }

      setLoadingRoutes(true);
      const computed = [];

      for (let i = 0; i < validStops.length - 1; i++) {
        const stopA = validStops[i];
        const stopB = validStops[i + 1];

        const lat1 = stopA.city.latitude;
        const lon1 = stopA.city.longitude;
        const lat2 = stopB.city.latitude;
        const lon2 = stopB.city.longitude;

        const mode = getLegMode(stopA, stopB);

        try {
          const routeResult = await getLegRouteGeometry(lat1, lon1, lat2, lon2, mode);
          computed.push({
            id: `${stopA.id}_${stopB.id}`,
            fromName: stopA.city.name,
            toName: stopB.city.name,
            mode: routeResult.mode,
            coordinates: routeResult.coordinates,
          });
        } catch (err) {
          // Fallback straight segment if calculation error
          computed.push({
            id: `${stopA.id}_${stopB.id}`,
            fromName: stopA.city.name,
            toName: stopB.city.name,
            mode: mode,
            coordinates: [[lat1, lon1], [lat2, lon2]],
          });
        }
      }

      if (isMounted) {
        setLegRoutes(computed);
        setLoadingRoutes(false);
      }
    }

    computeRoutes();

    return () => {
      isMounted = false;
    };
  }, [stops, trip?.transit_legs, trip?.transit_mode]);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <MapContainer
        center={center}
        zoom={5}
        style={{ width: "100%", height: "100%", borderRadius: "var(--radius-card)", background: "#16171d" }}
        zoomControl={true}
      >
        {/* Luxury High-Contrast Dark Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* Multi-Modal Mode-Aware Polylines */}
        {legRoutes.map((leg) => {
          if (leg.mode === "flight") {
            // Flight: Geodesic curved arc with bright cyan color and flight dashes
            return (
              <Polyline
                key={leg.id}
                positions={leg.coordinates}
                pathOptions={{
                  color: "#38bdf8",
                  weight: 3.5,
                  opacity: 0.9,
                  dashArray: "8 8",
                  lineCap: "round",
                }}
              />
            );
          }

          if (leg.mode === "train") {
            // Train: Dual-layer railway line (amber base + white railway tie dashes)
            return (
              <div key={leg.id}>
                <Polyline
                  positions={leg.coordinates}
                  pathOptions={{
                    color: "#f59e0b",
                    weight: 5,
                    opacity: 0.95,
                    lineCap: "round",
                  }}
                />
                <Polyline
                  positions={leg.coordinates}
                  pathOptions={{
                    color: "#ffffff",
                    weight: 2,
                    opacity: 0.85,
                    dashArray: "4 12",
                  }}
                />
              </div>
            );
          }

          // Road / Bus / Cab: Real turn-by-turn highway geometry
          return (
            <Polyline
              key={leg.id}
              positions={leg.coordinates}
              pathOptions={{
                color: "#10b981",
                weight: 4,
                opacity: 0.95,
                lineCap: "round",
                lineJoin: "round",
              }}
            />
          );
        })}

        {/* Unified Luxury City Pin Markers */}
        {validStops.map((stop, idx) => (
          <Marker
            key={stop.id}
            position={[stop.city.latitude, stop.city.longitude]}
            icon={createUnifiedCityMarker(stop.city.name, idx + 1, stop.id === selectedStopId)}
            eventHandlers={{ click: () => onStopClick?.(stop) }}
          >
            <Popup>
              <div style={{ fontFamily: "DM Sans, sans-serif", padding: "4px 2px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <span style={{
                    background: "#292928",
                    color: "#c3f832",
                    fontSize: 10,
                    fontWeight: 800,
                    padding: "2px 6px",
                    borderRadius: 999
                  }}>
                    Stop {idx + 1}
                  </span>
                  <strong style={{ fontSize: 14, color: "#191919" }}>{stop.city.name}</strong>
                </div>
                <p style={{ margin: "2px 0 0", fontSize: 12, color: "#5c5c5b" }}>
                  {stop.arrival_date} → {stop.departure_date}
                </p>
                <p style={{ margin: "4px 0 0", fontSize: 11, color: "#888" }}>
                  {stop.city.country}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        <FitBounds coords={coords} />
      </MapContainer>

      {/* Mode Route Legend HUD */}
      {validStops.length >= 2 && (
        <div style={{
          position: "absolute",
          top: 16,
          right: 16,
          zIndex: 1000,
          background: "rgba(25, 25, 25, 0.9)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: "var(--radius-input)",
          padding: "10px 14px",
          display: "flex",
          flexDirection: "column",
          gap: 6,
          boxShadow: "0 8px 24px rgba(0, 0, 0, 0.35)",
        }}>
          <span style={{ fontSize: "10px", fontWeight: 700, color: "#a1a1aa", textTransform: "uppercase", letterSpacing: "0.5px" }}>
            Live Route Vectors
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: "11px", fontWeight: 600, color: "#ffffff" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 14, height: 3, background: "#10b981", borderRadius: 2 }} />
              <span>Road / Cab</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 14, height: 3, background: "#f59e0b", borderRadius: 2 }} />
              <span>Train</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 14, height: 3, background: "#38bdf8", borderTop: "1px dashed #38bdf8" }} />
              <span>Flight</span>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {coords.length === 0 && (
        <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", zIndex: 1000, pointerEvents: "none" }}>
          <div className="card" style={{ padding: "24px 32px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12, textAlign: "center", boxShadow: "var(--shadow-float)", pointerEvents: "auto" }}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "var(--surface)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <MapPin size={24} color="var(--ink-soft)" />
            </div>
            <p style={{ fontWeight: 600, color: "var(--ink)", fontSize: "1rem" }}>Add destinations to see realistic live routes on the map</p>
          </div>
        </div>
      )}
    </div>
  );
}
