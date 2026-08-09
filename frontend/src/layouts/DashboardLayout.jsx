import { Outlet } from "react-router-dom";
import { useState } from "react";

import Sidebar from "../components/Sidebar/Sidebar";
import Header from "../components/Header/Header";

const DashboardLayout = () => {

    const [
        sidebarCollapsed,
        setSidebarCollapsed
    ] = useState(false);


    return (

        <div
            className={`app-layout ${
                sidebarCollapsed
                    ? "sidebar-is-collapsed"
                    : "sidebar-is-expanded"
            }`}
        >

            {/* =====================================================
                SIDEBAR
            ===================================================== */}

            <Sidebar
                collapsed={sidebarCollapsed}
                setCollapsed={setSidebarCollapsed}
            />


            {/* =====================================================
                MAIN APPLICATION AREA
            ===================================================== */}

            <div className="main-layout">


                {/* =================================================
                    GLOBAL HEADER
                ================================================= */}

                <Header />


                {/* =================================================
                    PAGE CONTENT
                ================================================= */}

                <main className="content-area">

                    <Outlet />

                </main>


            </div>

        </div>

    );

};


export default DashboardLayout;