import { useState } from "react";
import { Link } from "react-router-dom";
import { Mail } from "lucide-react";
import { authService } from "../services/authService";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function ForgotPasswordPage() {
  const [email, setEmail]   = useState("");
  const [sent, setSent]     = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  async function handleSubmit(e) {
    e.preventDefault(); setLoading(true); setError("");
    try { await authService.forgotPassword(email); setSent(true); }
    catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--surface)", padding: 24 }}>
      <div className="card" style={{ width: "min(440px, 100%)", padding: 40 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 32 }}>
          <div style={{ width: 32, height: 32, background: "var(--ink)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 14, color: "var(--accent)" }}>T</div>
          <span style={{ fontWeight: 700, fontSize: "1.125rem", letterSpacing: "-0.02em" }}>TRIPORA</span>
        </div>
        {sent ? (
          <div style={{ textAlign: "center" }}>
            <Mail size={40} color="var(--accent)" style={{ margin: "0 auto 16px" }} />
            <h2>Check your email</h2>
            <p style={{ color: "var(--ink-soft)", marginTop: 8 }}>We sent a reset link to <strong>{email}</strong></p>
            <Link to="/login" className="btn btn--primary" style={{ marginTop: 24, display: "inline-flex", justifyContent: "center" }}>Back to login</Link>
          </div>
        ) : (
          <>
            <h2>Reset password</h2>
            <p style={{ color: "var(--ink-soft)", marginTop: 8, marginBottom: 28 }}>Enter your email and we will send a reset link.</p>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div>
                <label className="label" htmlFor="fp-email">Email</label>
                <input id="fp-email" className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required autoFocus />
              </div>
              {error && <p style={{ color: "var(--danger)", fontSize: "0.875rem" }}>{error}</p>}
              <button className="btn btn--primary" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
                {loading ? <LoadingSpinner size={16} color="#fff" /> : "Send reset link"}
              </button>
            </form>
            <div style={{ marginTop: 24, textAlign: "center" }}>
              <Link to="/login" style={{ color: "var(--ink-soft)", fontSize: "0.875rem" }}>← Back to login</Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
