import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Globe } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function SignupPage() {
  const { signup }   = useAuth();
  const { addToast } = useToast();
  const navigate     = useNavigate();

  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [error, setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    if (form.password !== form.confirm) { setError("Passwords do not match"); return; }
    setError(""); setLoading(true);
    try {
      await signup({ name: form.full_name, full_name: form.full_name, email: form.email, password: form.password });
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
      addToast({ message: err.message, type: "error" });
    } finally { setLoading(false); }
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <div style={{
        flex: 1, 
        background: "url(https://images.unsplash.com/photo-1506929562872-bb421503ef21?q=80&w=2000&auto=format&fit=crop) center/cover",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", padding: 48,
        position: "relative", overflow: "hidden",
      }} className="hide-mobile">
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.8) 100%)" }} />
        <Globe size={64} color="var(--accent)" style={{ marginBottom: 24, position: "relative" }} />
        <h1 style={{ color: "var(--white)", textAlign: "center", position: "relative", textShadow: "0 4px 20px rgba(0,0,0,0.3)" }}>Start your journey</h1>
        <p style={{ color: "rgba(255,255,255,0.8)", marginTop: 16, textAlign: "center", position: "relative", textShadow: "0 2px 10px rgba(0,0,0,0.5)", fontSize: "1.1rem" }}>
          AI-powered travel planning,<br />budget tracking, and city discovery.
        </p>
      </div>

      <div style={{ width: "min(480px, 100%)", padding: "48px 40px", display: "flex", flexDirection: "column", justifyContent: "center", background: "var(--white)" }}>
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24 }}>
            <div style={{ width: 32, height: 32, background: "var(--ink)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 14, color: "var(--accent)" }}>T</div>
            <span style={{ fontWeight: 700, fontSize: "1.125rem", letterSpacing: "-0.02em" }}>TRIPORA</span>
          </div>
          <h2>Create account</h2>
          <p style={{ color: "var(--ink-soft)", marginTop: 6 }}>Free forever. No credit card.</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label className="label" htmlFor="su-name">Full Name</label>
            <input id="su-name" className="input" type="text" value={form.full_name} onChange={set("full_name")} placeholder="Jane Doe" required />
          </div>
          <div>
            <label className="label" htmlFor="su-email">Email</label>
            <input id="su-email" className="input" type="email" value={form.email} onChange={set("email")} placeholder="you@example.com" required />
          </div>
          <div>
            <label className="label" htmlFor="su-pw">Password</label>
            <input id="su-pw" className="input" type="password" value={form.password} onChange={set("password")} placeholder="At least 8 chars" minLength={8} required />
          </div>
          <div>
            <label className="label" htmlFor="su-confirm">Confirm Password</label>
            <input id="su-confirm" className={`input ${error ? "input--error" : ""}`} type="password" value={form.confirm} onChange={set("confirm")} placeholder="Repeat password" required />
          </div>
          {error && <p style={{ color: "var(--danger)", fontSize: "0.875rem" }}>{error}</p>}
          <button className="btn btn--primary" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center", padding: "13px 20px", marginTop: 4 }}>
            {loading ? <LoadingSpinner size={16} color="#fff" /> : "Create account"}
          </button>
        </form>

        <p style={{ marginTop: 32, textAlign: "center", color: "var(--ink-soft)", fontSize: "0.875rem" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "var(--ink)", fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
      <style>{`@media (max-width: 768px) { .hide-mobile { display: none !important; } }`}</style>
    </div>
  );
}
