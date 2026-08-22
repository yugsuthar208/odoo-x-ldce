import { NavLink } from "react-router-dom";
import { LayoutDashboard, MapPin, Globe, User } from "lucide-react";

const TABS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Home"    },
  { to: "/trips",     icon: MapPin,          label: "Trips"   },
  { to: "/explore",   icon: Globe,           label: "Explore" },
  { to: "/profile",   icon: User,            label: "Profile" },
];

export function BottomTabBar() {
  return (
    <nav style={{
      position: "fixed", bottom: 0, left: 0, right: 0,
      background: "var(--white)",
      borderTop: "1px solid var(--border)",
      display: "flex",
      zIndex: 200,
      paddingBottom: "env(safe-area-inset-bottom, 0)",
    }}>
      {TABS.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          style={({ isActive }) => ({
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 3,
            padding: "10px 0",
            color: isActive ? "var(--ink)" : "var(--ink-soft)",
            transition: "color var(--t-fast)",
          })}
        >
          {({ isActive }) => (
            <>
              <Icon size={20} style={{ strokeWidth: isActive ? 2.2 : 1.5 }} />
              <span style={{ fontSize: "0.6875rem", fontWeight: isActive ? 600 : 400 }}>{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
