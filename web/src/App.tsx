import { useState } from "react";
import { BrowserRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import Feed from "./pages/Feed";
import Summaries from "./pages/Summaries";
import Runs from "./pages/Runs";
import Delivery from "./pages/Delivery";
import Analytics from "./pages/Analytics";
import Config from "./pages/Config";
import Health from "./pages/Health";

const navItems = [
  { to: "/", label: "Feed", end: true },
  { to: "/summaries", label: "Summaries" },
  { to: "/runs", label: "Runs" },
  { to: "/delivery", label: "Delivery" },
  { to: "/analytics", label: "Analytics" },
  { to: "/health", label: "Health" },
  { to: "/config", label: "Config" },
];

function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <aside style={{
      width: collapsed ? 60 : 220,
      background: "#0f172a",
      color: "#e2e8f0",
      minHeight: "100vh",
      padding: collapsed ? 8 : 16,
      transition: "width 0.2s",
      display: "flex",
      flexDirection: "column",
      gap: 4,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        {!collapsed && <strong style={{ fontSize: 16 }}>ScrawlNews</strong>}
        <button onClick={() => setCollapsed((v) => !v)} style={{ background: "none", border: "none", color: "#e2e8f0", cursor: "pointer" }}>
          {collapsed ? "▶" : "◀"}
        </button>
      </div>
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          style={({ isActive }) => ({
            display: "block",
            padding: "10px 12px",
            borderRadius: 6,
            color: isActive ? "#38bdf8" : "#cbd5e1",
            background: isActive ? "#1e293b" : "transparent",
            textDecoration: "none",
            fontSize: 14,
            whiteSpace: "nowrap",
            overflow: "hidden",
          })}
        >
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: 24, background: "#f8fafc", minHeight: "100vh" }}>
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/summaries" element={<Summaries />} />
          <Route path="/runs" element={<Runs />} />
          <Route path="/delivery" element={<Delivery />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/health" element={<Health />} />
          <Route path="/config" element={<Config />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
