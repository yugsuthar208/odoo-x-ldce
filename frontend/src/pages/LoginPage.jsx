import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Eye, EyeOff, Globe } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/common/Toast";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function LoginPage() {
  const { login }   = useAuth();
  const { addToast } = useToast();
  const navigate    = useNavigate();
  const location    = useLocation();
  const from        = location.state?.from?.pathname || "/dashboard";

  const [email, setEmail]     = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw]   = useState(false);
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
      addToast({ message: err.message, type: "error" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Left decorative panel */}
      <div style={{
        flex: 1, 
        background: "url(https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2000&auto=format&fit=crop) center/cover",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: 48,
        position: "relative", overflow: "hidden",
      }} className="hide-mobile">
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 100%)",
        }} />
        <Globe size={64} color="var(--accent)" style={{ marginBottom: 24, position: "relative" }} />
        <h1 style={{ color: "var(--white)", textAlign: "center", position: "relative", textShadow: "0 4px 20px rgba(0,0,0,0.3)" }}>
          Plan smarter.<br />Travel better.
        </h1>
        <p style={{ color: "rgba(255,255,255,0.8)", marginTop: 16, textAlign: "center", position: "relative", textShadow: "0 2px 10px rgba(0,0,0,0.5)", fontSize: "1.1rem" }}>
          Multi-city itineraries, AI budget prediction,<br />curated city experiences.
        </p>
      </div>

      {/* Right form panel */}
      <div style={{
        width: "min(480px, 100%)", padding: "48px 40px",
        display: "flex", flexDirection: "column", justifyContent: "center",
        background: "var(--white)",
      }}>
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24 }}>
            <div style={{
              width: 32, height: 32, background: "var(--ink)", borderRadius: 8,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 700, fontSize: 14, color: "var(--accent)",
            }}>T</div>
            <span style={{ fontWeight: 700, fontSize: "1.125rem", letterSpacing: "-0.02em" }}>TRIPORA</span>
          </div>
          <h2>Welcome back</h2>
          <p style={{ color: "var(--ink-soft)", marginTop: 6 }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div>
            <label className="label" htmlFor="login-email">Email</label>
            <input
              id="login-email" className={`input ${error ? "input--error" : ""}`}
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" required autoFocus
            />
          </div>
          <div>
            <label className="label" htmlFor="login-password">Password</label>
            <div style={{ position: "relative" }}>
              <input
                id="login-password" className={`input ${error ? "input--error" : ""}`}
                type={showPw ? "text" : "password"} value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" required style={{ paddingRight: 44 }}
              />
              <button type="button" onClick={() => setShowPw(!showPw)} style={{
                position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                color: "var(--ink-soft)", background: "none", border: "none", cursor: "pointer",
              }}>
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && <p style={{ color: "var(--danger)", fontSize: "0.875rem" }}>{error}</p>}

          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Link to="/forgot-password" style={{ fontSize: "0.875rem", color: "var(--ink-soft)" }}>
              Forgot password?
            </Link>
          </div>

          <button className="btn btn--primary" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center", padding: "13px 20px" }}>
            {loading ? <LoadingSpinner size={16} color="#fff" /> : "Sign in"}
          </button>
        </form>

        <p style={{ marginTop: 32, textAlign: "center", color: "var(--ink-soft)", fontSize: "0.875rem" }}>
          No account?{" "}
          <Link to="/signup" style={{ color: "var(--ink)", fontWeight: 600 }}>
            Create one
          </Link>
        </p>
      </div>

      <style>{`@media (max-width: 768px) { .hide-mobile { display: none !important; } }`}</style>
    </div>
  );
}
