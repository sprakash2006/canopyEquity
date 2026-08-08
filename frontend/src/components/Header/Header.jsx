import {
  Bell,
  Search,
  Moon,
  Sun,
  Wifi,
  Cpu,
} from "lucide-react";

import { useState } from "react";

import "./Header.css";

export default function Header() {

  const [dark, setDark] = useState(true);

  return (

    <header className="header">

      <div className="header-left">

        <h1>Dashboard</h1>

        <p>
          AI Powered Urban Tree Canopy Analysis
        </p>

      </div>

      <div className="header-center">

        <div className="search-box">

          <Search size={18} />

          <input
            type="text"
            placeholder="Search wards, reports..."
          />

        </div>

      </div>

      <div className="header-right">

        <div className="status backend">

          <Wifi size={16} />

          Backend Online

        </div>

        <div className="status model">

          <Cpu size={16} />

          AI Ready

        </div>

        <button
          className="theme-btn"
          onClick={() => setDark(!dark)}
        >
          {dark ? (
            <Sun size={18}/>
          ) : (
            <Moon size={18}/>
          )}
        </button>

        <button className="notify">

          <Bell size={20}/>

          <span></span>

        </button>

        <div className="profile">

          <img
            src="https://ui-avatars.com/api/?name=CanopyAI&background=22c55e&color=fff"
            alt=""
          />

          <div>

            <h4>Administrator</h4>

            <small>AI Engineer</small>

          </div>

        </div>

      </div>

    </header>

  );

}