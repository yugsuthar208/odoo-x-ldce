import { Loader2 } from "lucide-react";

export function LoadingSpinner({ size = 20, color = "currentColor" }) {
  return (
    <Loader2
      size={size}
      color={color}
      className="animate-spin"
      aria-label="Loading..."
    />
  );
}

export function PageLoader() {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      height: "100vh", width: "100%",
    }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
        <LoadingSpinner size={32} color="var(--ink)" />
        <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>Loading…</p>
      </div>
    </div>
  );
}
