import { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle, XCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);
let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ message, type = "success", duration = 3500 }) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), duration);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const icons = {
    success: <CheckCircle size={16} color="var(--accent)" />,
    error:   <XCircle size={16} color="var(--danger)" />,
    info:    <Info size={16} color="var(--ink-soft)" />,
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div style={{
        position: "fixed", bottom: 24, right: 24,
        display: "flex", flexDirection: "column", gap: 8,
        zIndex: 99999, maxWidth: 360,
      }}>
        {toasts.map((t) => (
          <div key={t.id} className="card animate-slideDown" style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "12px 16px",
            boxShadow: "var(--shadow-float)",
          }}>
            {icons[t.type]}
            <span style={{ flex: 1, fontSize: "0.875rem", fontWeight: 500 }}>{t.message}</span>
            <button className="btn btn--icon btn--ghost btn--sm" onClick={() => removeToast(t.id)}>
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be inside ToastProvider");
  return ctx;
}
