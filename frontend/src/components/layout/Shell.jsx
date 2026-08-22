import { Outlet, useNavigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { BottomTabBar } from "./BottomTabBar";
import { useAuth } from "../../context/AuthContext";
import { useEffect, useState } from "react";

export function Shell() {
  const { user } = useAuth();
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {!isMobile && <Sidebar />}

      {/* Sidebar width offset for content */}
      <main style={{
        flex: 1,
        marginLeft: isMobile ? 0 : "var(--sidebar-collapsed)",
        paddingBottom: isMobile ? 72 : 0,
        minWidth: 0,
        transition: "margin-left var(--t-normal)",
      }}>
        <Outlet />
      </main>

      {isMobile && <BottomTabBar />}

      {/* Sidebar hover label reveal: inject style once */}
      <style>{`
        .sidebar:hover .sidebar-label { opacity: 1 !important; }
      `}</style>
    </div>
  );
}
