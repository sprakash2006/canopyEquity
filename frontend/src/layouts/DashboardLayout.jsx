import { Outlet } from "react-router-dom";
import { useState } from "react";

import Sidebar from "../components/Sidebar/Sidebar";
import Header from "../components/Header/Header";


const DashboardLayout = () => {


    const [sidebarCollapsed,setSidebarCollapsed] = useState(false);


    return (

        <div className="app-layout">


            {/* SIDEBAR */}

            <Sidebar

                collapsed={sidebarCollapsed}

                setCollapsed={setSidebarCollapsed}

            />



            {/* RIGHT SIDE */}

            <div className="main-layout">


                <Header />



                <main className="content-area">


                    <Outlet />


                </main>


            </div>


        </div>

    );

};


export default DashboardLayout;