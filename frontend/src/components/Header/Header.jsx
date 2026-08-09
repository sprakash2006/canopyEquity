import {
    Bell,
    Search,
    Moon,
    Sun,
    Wifi,
    Cpu
} from "lucide-react";

import { useState } from "react";

import "./Header.css";


export default function Header() {

    const [dark, setDark] = useState(true);


    return (

        <header className="header">


            {/* =====================================================
                LEFT — PAGE TITLE
            ===================================================== */}

            <div className="header-left">

                <div className="header-title-row">

                    <h1>
                        Dashboard
                    </h1>


                    <span className="header-live-badge">

                        <span className="header-live-dot" />

                        LIVE

                    </span>

                </div>


                <p>
                    AI-powered urban tree canopy intelligence
                </p>

            </div>



            {/* =====================================================
                CENTER — SEARCH
            ===================================================== */}

            <div className="header-center">

                <div className="search-box">

                    <Search
                        size={17}
                        strokeWidth={2}
                    />


                    <input
                        type="text"
                        placeholder="Search wards, reports..."
                        aria-label="Search wards and reports"
                    />


                    <span className="search-shortcut">
                        ⌘ K
                    </span>

                </div>

            </div>



            {/* =====================================================
                RIGHT — SYSTEM STATUS
            ===================================================== */}

            <div className="header-right">


                {/* ================= BACKEND ================= */}

                <div className="status status-backend">

                    <span className="status-icon">

                        <Wifi
                            size={14}
                            strokeWidth={2}
                        />

                    </span>


                    <span className="status-content">

                        <span className="status-label">
                            Backend
                        </span>


                        <span className="status-value">

                            <span className="status-dot online" />

                            Online

                        </span>

                    </span>

                </div>



                {/* ================= AI ENGINE ================= */}

                <div className="status status-model">

                    <span className="status-icon">

                        <Cpu
                            size={14}
                            strokeWidth={2}
                        />

                    </span>


                    <span className="status-content">

                        <span className="status-label">
                            AI Engine
                        </span>


                        <span className="status-value">

                            <span className="status-dot online" />

                            Ready

                        </span>

                    </span>

                </div>



                {/* ================= DIVIDER ================= */}

                <div className="header-divider" />



                {/* ================= THEME ================= */}

                <button
                    type="button"
                    className="header-icon-btn"
                    onClick={() =>
                        setDark(!dark)
                    }
                    aria-label="Toggle theme"
                    title="Toggle theme"
                >

                    {dark ? (

                        <Sun
                            size={18}
                            strokeWidth={1.9}
                        />

                    ) : (

                        <Moon
                            size={18}
                            strokeWidth={1.9}
                        />

                    )}

                </button>



                {/* ================= NOTIFICATIONS ================= */}

                <button
                    type="button"
                    className="header-icon-btn notification-btn"
                    aria-label="Notifications"
                    title="Notifications"
                >

                    <Bell
                        size={18}
                        strokeWidth={1.9}
                    />


                    <span className="notification-dot" />

                </button>



                {/* =================================================
                    PROFILE
                ================================================= */}

                <div className="header-profile">

                    <div className="header-avatar">
                        C
                    </div>


                    <div className="header-profile-info">

                        <strong>
                            Administrator
                        </strong>


                        <span>
                            AI Engineer
                        </span>

                    </div>

                </div>


            </div>


        </header>

    );

}