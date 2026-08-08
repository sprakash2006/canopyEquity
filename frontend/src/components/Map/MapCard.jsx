import "./MapCard.css";

import {
    Layers3,
    Satellite,
    Maximize2,
    RefreshCw
} from "lucide-react";

import GISMap from "../GISMap/GISMap";

export default function MapCard() {

    return (

        <div className="map-card">

            {/* ================= HEADER ================= */}

            <div className="map-header">

                <div>

                    <h2>Interactive GIS Map</h2>

                    <p>

                        AI Prediction • Satellite • Ward Boundaries

                    </p>

                </div>

                <div className="map-actions">

                    <button>

                        <Layers3 size={18}/>

                        Layers

                    </button>

                    <button>

                        <Satellite size={18}/>

                        Satellite

                    </button>

                    <button>

                        <RefreshCw size={18}/>

                    </button>

                    <button>

                        <Maximize2 size={18}/>

                    </button>

                </div>

            </div>

            {/* ================= MAP ================= */}

            <div className="map-body">

                <GISMap />

            </div>

            {/* ================= LEGEND ================= */}

            <div className="legend">

                <div>

                    <span className="green"></span>

                    Dense Canopy

                </div>

                <div>

                    <span className="yellow"></span>

                    Sparse Vegetation

                </div>

                <div>

                    <span className="blue"></span>

                    Water

                </div>

                <div>

                    <span className="gray"></span>

                    Urban Area

                </div>

            </div>

        </div>

    );

}