import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { LoadingSpinner } from "./LoadingSpinner";

export function ConfirmDialog({ isOpen, title, description, onConfirm, onCancel, confirmLabel = "Delete", dangerous = true }) {
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setLoading(true);
    try { await onConfirm(); }
    finally { setLoading(false); }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 9999,
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <div
        style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.4)", backdropFilter: "blur(4px)" }}
        onClick={onCancel}
      />
      <div className="card animate-fadeUp" style={{
        position: "relative", zIndex: 1,
        width: "min(420px, 90vw)", padding: 28,
        display: "flex", flexDirection: "column", gap: 20,
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
          <div style={{
            width: 40, height: 40, flexShrink: 0,
            background: dangerous ? "#fff0f0" : "#fffbeb",
            borderRadius: "50%",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <AlertTriangle size={18} color={dangerous ? "var(--danger)" : "var(--warn)"} />
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ marginBottom: 6 }}>{title}</h3>
            <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>{description}</p>
          </div>
          <button className="btn btn--icon btn--ghost" onClick={onCancel} style={{ flexShrink: 0 }}>
            <X size={16} />
          </button>
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <button className="btn btn--ghost btn--sm" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button
            className={`btn btn--sm ${dangerous ? "btn--danger" : "btn--primary"}`}
            onClick={handleConfirm}
            disabled={loading}
          >
            {loading ? <LoadingSpinner size={14} color="#fff" /> : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
