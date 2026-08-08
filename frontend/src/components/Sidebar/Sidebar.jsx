import {
  LayoutDashboard,
  Upload,
  BrainCircuit,
  Map,
  Trophy,
  Trees,
  FileBarChart2,
  Download,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import { NavLink } from "react-router-dom";
import { useState } from "react";

import "./Sidebar.css";

const menuItems = [
  {
    title: "Dashboard",
    icon: LayoutDashboard,
    path: "/",
  },
  {
    title: "Upload Raster",
    icon: Upload,
    path: "/upload",
  },
  {
    title: "AI Analysis",
    icon: BrainCircuit,
    path: "/analysis",
  },
  {
    title: "Map Viewer",
    icon: Map,
    path: "/map",
  },
  {
    title: "Ward Ranking",
    icon: Trophy,
    path: "/ranking",
  },
  {
    title: "Recommendations",
    icon: Trees,
    path: "/recommendations",
  },
  {
    title: "Reports",
    icon: FileBarChart2,
    path: "/reports",
  },
  {
    title: "Downloads",
    icon: Download,
    path: "/downloads",
  },
  {
    title: "Settings",
    icon: Settings,
    path: "/settings",
  },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`sidebar ${
        collapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <div className="sidebar-top">

        <div className="logo-area">

          <div className="logo-circle">
            🌳
          </div>

          {!collapsed && (
            <div>
              <h2>CanopyAI</h2>
              <span>Urban Intelligence</span>
            </div>
          )}

        </div>

        <button
          className="collapse-btn"
          onClick={() =>
            setCollapsed(!collapsed)
          }
        >
          {collapsed ? (
            <ChevronRight size={18} />
          ) : (
            <ChevronLeft size={18} />
          )}
        </button>

      </div>

      <nav className="menu">

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                isActive
                  ? "menu-item active"
                  : "menu-item"
              }
            >
              <Icon size={20} />

              {!collapsed && (
                <span>{item.title}</span>
              )}
            </NavLink>
          );
        })}

      </nav>

      <div className="sidebar-footer">

        <div className="avatar">
          S
        </div>

        {!collapsed && (
          <div>
            <h4>Administrator</h4>
            <small>AI Engineer</small>
          </div>
        )}

      </div>
    </aside>
  );
}