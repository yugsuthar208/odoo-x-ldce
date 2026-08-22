import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { User, Mail, DollarSign, Globe, Check, LogOut, Shield } from "lucide-react";
import { useToast } from "../components/common/Toast";

const CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD", "SGD", "CHF"];

export default function ProfilePage() {
  const { user, logout, updateProfile } = useAuth();
  const { addToast } = useToast();

  const [name, setName] = useState("");
  const [preferredCurrency, setPreferredCurrency] = useState("USD");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setName(user.name || user.full_name || "");
      setPreferredCurrency(user.preferred_currency || "USD");
    }
  }, [user]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfile({ name: name.trim(), preferred_currency: preferredCurrency });
      addToast({ message: "Profile updated successfully!" });
    } catch (err) {
      console.error(err);
      addToast({ message: err.message || "Failed to update profile", type: "error" });
    } finally {
      setSaving(false);
    }
  };

  const displayName = user?.name || user?.full_name || "Traveler";
  const initials = displayName.substring(0, 2).toUpperCase();

  return (
    <div className="page fade-in" style={{ maxWidth: 680 }}>
      <h1 style={{ marginBottom: 8 }}>Account Settings</h1>
      <p style={{ color: "var(--ink-soft)", marginBottom: 32 }}>Manage your personal details and travel preferences.</p>

      {/* Profile Overview Card */}
      <div className="card" style={{ padding: 28, marginBottom: 24, display: "flex", alignItems: "center", gap: 20 }}>
        <div style={{
          width: 64, height: 64, borderRadius: "50%",
          background: "var(--primary-surface)", color: "var(--primary-main)",
          fontSize: "1.5rem", fontWeight: 700,
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0
        }}>
          {initials}
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: "1.25rem", marginBottom: 4 }}>{displayName}</h2>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--ink-soft)", fontSize: "0.875rem" }}>
            <Mail size={14} /> {user?.email}
          </div>
        </div>
        <button className="btn btn--danger btn--sm" onClick={logout} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <LogOut size={16} /> Sign out
        </button>
      </div>

      {/* Edit Profile Form */}
      <form onSubmit={handleSave} className="card" style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20 }}>
        <h3 style={{ fontSize: "1.1rem", borderBottom: "1px solid var(--border)", paddingBottom: 12 }}>Personal Preferences</h3>

        <div>
          <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <User size={14} /> Full Name
          </label>
          <input 
            type="text" 
            className="input" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
            placeholder="Your Name"
            required 
          />
        </div>

        <div>
          <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Mail size={14} /> Email Address
          </label>
          <input 
            type="email" 
            className="input" 
            value={user?.email || ""} 
            disabled 
            style={{ background: "var(--surface)", cursor: "not-allowed" }}
          />
          <span style={{ fontSize: "0.75rem", color: "var(--ink-soft)", marginTop: 4, display: "block" }}>
            Email address cannot be changed.
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <DollarSign size={14} /> Preferred Currency
            </label>
            <select 
              className="input" 
              value={preferredCurrency} 
              onChange={(e) => setPreferredCurrency(e.target.value)}
            >
              {CURRENCIES.map(curr => (
                <option key={curr} value={curr}>{curr}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Globe size={14} /> Interface Language
            </label>
            <select className="input" defaultValue="en" disabled style={{ background: "var(--surface)" }}>
              <option value="en">English (US)</option>
            </select>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
          <button type="submit" className="btn btn--primary" disabled={saving} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Check size={16} /> {saving ? "Saving Changes..." : "Save Preferences"}
          </button>
        </div>
      </form>
    </div>
  );
}
