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


export default function Sidebar({
    collapsed = false,
    setCollapsed,
}) {

    const handleCollapse = () => {

        if (setCollapsed) {

            setCollapsed(!collapsed);

        }

    };


    return (

        <aside
            className={`sidebar ${
                collapsed
                    ? "sidebar-collapsed"
                    : ""
            }`}
        >

            {/* =====================================================
                BRAND
            ===================================================== */}

            <div className="sidebar-brand">

                <div className="brand-mark">

                    <Trees
                        size={22}
                        strokeWidth={2.2}
                    />

                </div>


                {!collapsed && (

                    <div className="brand-copy">

                        <h2>
                            Canopy<span>AI</span>
                        </h2>

                        <p>
                            Urban Intelligence
                        </p>

                    </div>

                )}

            </div>


            {/* =====================================================
                COLLAPSE BUTTON
            ===================================================== */}

            <button
                type="button"
                className="sidebar-collapse-btn"
                onClick={handleCollapse}
                aria-label={
                    collapsed
                        ? "Expand sidebar"
                        : "Collapse sidebar"
                }
                title={
                    collapsed
                        ? "Expand sidebar"
                        : "Collapse sidebar"
                }
            >

                {collapsed ? (

                    <ChevronRight
                        size={17}
                        strokeWidth={2}
                    />

                ) : (

                    <ChevronLeft
                        size={17}
                        strokeWidth={2}
                    />

                )}

            </button>


            {/* =====================================================
                NAVIGATION
            ===================================================== */}

            <nav
                className="sidebar-navigation"
                aria-label="Main navigation"
            >

                <div className="sidebar-section-label">

                    {!collapsed && (
                        <span>WORKSPACE</span>
                    )}

                </div>


                {menuItems.map((item) => {

                    const Icon = item.icon;


                    return (

                        <NavLink
                            key={item.title}
                            to={item.path}
                            end={item.path === "/"}
                            className={({ isActive }) =>
                                `sidebar-menu-item ${
                                    isActive
                                        ? "active"
                                        : ""
                                }`
                            }
                            title={
                                collapsed
                                    ? item.title
                                    : undefined
                            }
                        >

                            <span className="sidebar-icon">

                                <Icon
                                    size={19}
                                    strokeWidth={1.9}
                                />

                            </span>


                            {!collapsed && (

                                <span className="sidebar-menu-text">

                                    {item.title}

                                </span>

                            )}

                        </NavLink>

                    );

                })}

            </nav>


            {/* =====================================================
                FOOTER / USER
            ===================================================== */}

            <div className="sidebar-bottom">

                <div className="sidebar-user">

                    <div className="sidebar-avatar">
                        S
                    </div>


                    {!collapsed && (

                        <div className="sidebar-user-info">

                            <strong>
                                Administrator
                            </strong>

                            <span>
                                AI Engineer
                            </span>

                        </div>

                    )}

                </div>

            </div>

        </aside>

    );

}