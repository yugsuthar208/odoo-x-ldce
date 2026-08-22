import { AlertCircle, RefreshCcw } from "lucide-react";

export function ErrorState({ message = "Something went wrong", onRetry }) {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 16,
      padding: "48px 24px",
      textAlign: "center",
      color: "var(--ink-soft)",
    }}>
      <div style={{
        width: 56, height: 56,
        background: "#fff0f0",
        borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <AlertCircle size={24} color="var(--danger)" />
      </div>
      <div>
        <p style={{ fontWeight: 600, color: "var(--ink)", marginBottom: 4 }}>Oops!</p>
        <p style={{ fontSize: "0.875rem" }}>{message}</p>
      </div>
      {onRetry && (
        <button className="btn btn--ghost btn--sm" onClick={onRetry}>
          <RefreshCcw size={14} />
          Try again
        </button>
      )}
    </div>
  );
}
