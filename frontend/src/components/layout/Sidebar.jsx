import { NavLink } from "react-router-dom";
import { LayoutDashboard, MapPin, Globe, User } from "lucide-react";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/trips",     icon: MapPin,          label: "My Trips"  },
  { to: "/explore",   icon: Globe,           label: "Explore"   },
  { to: "/profile",   icon: User,            label: "Profile"   },
];

export function Sidebar() {
  return (
    <aside style={{
      width: "var(--sidebar-collapsed)",
      minHeight: "100vh",
      background: "var(--ink)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      paddingTop: 20,
      paddingBottom: 20,
      position: "fixed",
      left: 0, top: 0, bottom: 0,
      zIndex: 100,
      overflow: "hidden",
      transition: "width var(--t-normal)",
    }}
    className="sidebar"
    onMouseEnter={(e) => { e.currentTarget.style.width = "var(--sidebar-expanded)"; }}
    onMouseLeave={(e) => { e.currentTarget.style.width = "var(--sidebar-collapsed)"; }}
    >
      {/* Logo */}
      <div style={{
        width: "100%", padding: "4px 0 28px",
        display: "flex", alignItems: "center",
        gap: 10, paddingLeft: 18, overflow: "hidden",
      }}>
        <div style={{
          width: 28, height: 28, flexShrink: 0,
          background: "var(--accent)", borderRadius: 8,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontWeight: 700, fontSize: 13, color: "var(--ink)",
        }}>T</div>
        <span style={{
          color: "var(--accent)", fontWeight: 700, fontSize: "1rem",
          whiteSpace: "nowrap", letterSpacing: "-0.02em",
          opacity: 0, transition: "opacity var(--t-normal)",
        }} className="sidebar-label">TRIPORA</span>
      </div>

      {/* Nav items */}
      <nav style={{ width: "100%", display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 18px",
              position: "relative",
              color: isActive ? "var(--accent)" : "rgba(255,255,255,0.5)",
              transition: "color var(--t-fast)",
              overflow: "hidden",
              borderRadius: 0,
            })}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div style={{
                    position: "absolute", left: 0, top: "20%", bottom: "20%",
                    width: 3, background: "var(--accent)", borderRadius: "0 3px 3px 0",
                  }} />
                )}
                <Icon size={20} style={{ flexShrink: 0 }} />
                <span style={{
                  whiteSpace: "nowrap", fontWeight: 500, fontSize: "0.9375rem",
                  opacity: 0, transition: "opacity var(--t-normal)",
                }} className="sidebar-label">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
