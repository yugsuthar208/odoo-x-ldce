import { useState, useEffect } from "react";
import { tripService } from "../../services/tripService";
import { Users, Link as LinkIcon, UserPlus, Shield, ShieldAlert, Trash2, Check, Copy } from "lucide-react";

export default function TripCollab({ tripId, visibility }) {
  const [collaborators, setCollaborators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("editor");
  const [shareLink, setShareLink] = useState("");
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    loadCollaborators();
  }, [tripId]);

  const loadCollaborators = async () => {
    try {
      const res = await tripService.getCollaborators(tripId);
      const data = res?.data || (Array.isArray(res) ? res : []);
      setCollaborators(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setCollaborators([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCollab = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      await tripService.addCollaborator(tripId, { email: email.trim(), role });
      setEmail("");
      loadCollaborators();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "User not found or cannot be added");
    }
  };

  const handleRemoveCollab = async (userId) => {
    try {
      await tripService.removeCollaborator(tripId, userId);
      loadCollaborators();
    } catch (err) {
      console.error(err);
    }
  };

  const generateLink = async () => {
    try {
      const res = await tripService.generateShareLink(tripId, { expires_in_days: 7 });
      const payload = res?.data || res;
      const token = payload?.share_token || payload?.token;
      const fullUrl = `${window.location.origin}/shared/${token}`;
      setShareLink(fullUrl);
    } catch (err) {
      console.error(err);
      alert("Failed to generate share link.");
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fade-in" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
      
      {/* Collaborators List */}
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
          <Users size={20} className="text-primary" /> Trip Collaborators
        </h3>

        {collaborators.length === 0 && !loading && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", position: "relative", width: 80, height: 48, marginBottom: 16 }}>
              <div style={{ width: 48, height: 48, borderRadius: "50%", border: "2px dashed var(--border)", position: "absolute", left: 0, background: "var(--surface)" }} />
              <div style={{ width: 48, height: 48, borderRadius: "50%", border: "2px dashed var(--border)", position: "absolute", right: 0, background: "var(--surface)" }} />
              <UserPlus size={20} color="var(--ink-soft)" style={{ position: "relative", zIndex: 1 }} />
            </div>
            <p style={{ color: "var(--ink-soft)", fontSize: "0.9375rem" }}>Invite your first collaborator</p>
          </div>
        )}

        <form onSubmit={handleAddCollab} style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 24 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <input 
              type="email" 
              className="input" 
              placeholder="Enter traveler's email..." 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ flex: 1 }}
              required
            />
            <select className="input" value={role} onChange={(e) => setRole(e.target.value)} style={{ width: 110 }}>
              <option value="editor">Editor</option>
              <option value="viewer">Viewer</option>
            </select>
            <button type="submit" className="btn btn--primary btn--icon" title="Add Collaborator">
              <UserPlus size={18} />
            </button>
          </div>
          {errorMsg && (
            <span style={{ color: "var(--error-main)", fontSize: "0.8125rem" }}>{errorMsg}</span>
          )}
        </form>

        {loading ? (
          <p style={{ color: "var(--ink-soft)" }}>Loading collaborators...</p>
        ) : collaborators.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {collaborators.map((c) => {
              const displayName = c.user?.name || c.user?.email || `User ${c.user_id?.substring(0, 6)}`;
              const displayEmail = c.user?.email || "";
              const initials = (c.user?.name || c.user?.email || "U").substring(0, 2).toUpperCase();

              return (
                <div key={c.id || c.user_id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", background: "var(--surface)", borderRadius: "var(--radius-md)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: "50%", background: "var(--primary-surface)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--primary-main)", fontWeight: "bold", fontSize: "0.875rem" }}>
                      {initials}
                    </div>
                    <div>
                      <div style={{ fontWeight: "500", color: "var(--ink-dark)" }}>{displayName}</div>
                      {displayEmail && <div style={{ fontSize: "0.75rem", color: "var(--ink-soft)" }}>{displayEmail}</div>}
                      <div style={{ fontSize: "0.75rem", color: "var(--ink-soft)", display: "flex", alignItems: "center", gap: 4, marginTop: 2 }}>
                        {c.role === "editor" ? <Shield size={12} className="text-primary" /> : <ShieldAlert size={12} />} 
                        <span style={{ textTransform: "capitalize" }}>{c.role}</span>
                      </div>
                    </div>
                  </div>
                  <button className="btn btn--icon btn--ghost btn--sm" onClick={() => handleRemoveCollab(c.user_id)} title="Remove Collaborator">
                    <Trash2 size={16} color="var(--error-main)" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Public Share Link */}
      <div className="card" style={{ padding: 24, alignSelf: "start" }}>
        <h3 style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <LinkIcon size={20} className="text-primary" /> Public Share Link
        </h3>
        <p style={{ color: "var(--ink-soft)", fontSize: "0.875rem", marginBottom: 20 }}>
          Generate a read-only public link to share your itinerary with family and friends. Anyone with the link can view the trip without logging in.
        </p>

        {shareLink ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", gap: 8 }}>
              <input 
                type="text" 
                className="input" 
                value={shareLink} 
                readOnly 
                style={{ flex: 1, background: "var(--surface)", fontSize: "0.875rem" }}
              />
              <button className="btn btn--secondary" onClick={copyToClipboard} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                {copied ? <Check size={16} /> : <Copy size={16} />} {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--ink-soft)" }}>
              Link is active and valid for 7 days.
            </p>
          </div>
        ) : (
          <button className="btn btn--primary" onClick={generateLink}>Generate Share Link</button>
        )}
      </div>

    </div>
  );
}
