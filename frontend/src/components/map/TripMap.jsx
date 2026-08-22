import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapPin } from "lucide-react";

// Fix default leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:       "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:     "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function createCityIcon(label, isSelected) {
  return L.divIcon({
    className: "",
    html: `
      <div style="
        background: ${isSelected ? "#c3f832" : "#292928"};
        color: ${isSelected ? "#292928" : "#fff"};
        padding: 4px 10px;
        border-radius: 999px;
        font-family: DM Sans, sans-serif;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 2px solid ${isSelected ? "#292928" : "transparent"};
      ">${label}</div>`,
    iconAnchor: [0, 0],
  });
}

function FitBounds({ coords }) {
  const map = useMap();
  useEffect(() => {
    if (coords.length >= 2) {
      map.fitBounds(coords, { padding: [48, 48] });
    } else if (coords.length === 1) {
      map.setView(coords[0], 8);
    }
  }, [coords, map]);
  return null;
}

export function TripMap({ stops = [], selectedStopId = null, onStopClick }) {
  const coords = stops
    .filter((s) => s.city?.latitude && s.city?.longitude)
    .sort((a, b) => a.stop_order - b.stop_order)
    .map((s) => [s.city.latitude, s.city.longitude]);

  const center = coords.length > 0 ? coords[0] : [20, 0];
  const validStops = stops.filter((s) => s.city?.latitude && s.city?.longitude).sort((a, b) => a.stop_order - b.stop_order);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <MapContainer
        center={center}
        zoom={4}
        style={{ width: "100%", height: "100%", borderRadius: "var(--radius-card)" }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
        />

        {coords.length >= 2 && (
          <Polyline
            positions={coords}
            pathOptions={{
              color: "#c3f832",
              weight: 2.5,
              opacity: 0.85,
              dashArray: "10 6",
            }}
          />
        )}

        {validStops.map((stop) => (
          <Marker
            key={stop.id}
            position={[stop.city.latitude, stop.city.longitude]}
            icon={createCityIcon(stop.city.name, stop.id === selectedStopId)}
            eventHandlers={{ click: () => onStopClick?.(stop) }}
          >
            <Popup>
              <div style={{ fontFamily: "DM Sans, sans-serif" }}>
                <strong>{stop.city.name}</strong>
                <p style={{ margin: "4px 0 0", fontSize: 12, color: "#5c5c5b" }}>
                  {stop.arrival_date} → {stop.departure_date}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        <FitBounds coords={coords} />
      </MapContainer>

      {coords.length === 0 && (
        <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", zIndex: 1000, pointerEvents: "none" }}>
          <div className="card" style={{ padding: "24px 32px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12, textAlign: "center", boxShadow: "var(--shadow-float)", pointerEvents: "auto" }}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "var(--surface)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <MapPin size={24} color="var(--ink-soft)" />
            </div>
            <p style={{ fontWeight: 600, color: "var(--ink)", fontSize: "1rem" }}>Add your first stop to see it on the map</p>
          </div>
        </div>
      )}
    </div>
  );
}
