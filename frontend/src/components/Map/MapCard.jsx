import "./MapCard.css";

import {
    Layers3,
    Satellite,
    Maximize2,
    RefreshCw,
    MapPinned,
    Activity
} from "lucide-react";

import GISMap from "../GISMap/GISMap";


export default function MapCard() {

    return (

        <div className="map-card">

            {/* =================================================
                MAP HEADER
            ================================================= */}

            <div className="map-header">

                <div className="map-header-title">

                    <div className="map-title-icon">

                        <MapPinned
                            size={17}
                            strokeWidth={2}
                        />

                    </div>


                    <div>

                        <h2>
                            Interactive GIS Map
                        </h2>

                        <p>
                            AI prediction · satellite imagery · spatial intelligence
                        </p>

                    </div>

                </div>


                {/* =================================================
                    MAP ACTIONS
                ================================================= */}

                <div className="map-actions">

                    <button
                        type="button"
                        title="Layers"
                        aria-label="Layers"
                    >

                        <Layers3
                            size={16}
                            strokeWidth={1.9}
                        />

                        <span>
                            Layers
                        </span>

                    </button>


                    <button
                        type="button"
                        title="Satellite"
                        aria-label="Satellite"
                    >

                        <Satellite
                            size={16}
                            strokeWidth={1.9}
                        />

                        <span>
                            Satellite
                        </span>

                    </button>


                    <button
                        type="button"
                        className="map-icon-button"
                        title="Refresh map"
                        aria-label="Refresh map"
                    >

                        <RefreshCw
                            size={16}
                            strokeWidth={1.9}
                        />

                    </button>


                    <button
                        type="button"
                        className="map-icon-button"
                        title="Fullscreen"
                        aria-label="Fullscreen"
                    >

                        <Maximize2
                            size={16}
                            strokeWidth={1.9}
                        />

                    </button>

                </div>

            </div>


            {/* =================================================
                MAP
            ================================================= */}

            <div className="map-body">

                <GISMap />

            </div>


            {/* =================================================
                MAP STATUS BAR
            ================================================= */}

            <div className="map-status-bar">


                <div className="map-status-left">

                    <div className="map-status-item">

                        <span className="map-status-dot active" />

                        <span>
                            AI Prediction
                        </span>

                    </div>


                    <div className="map-status-item">

                        <span className="map-status-dot canopy" />

                        <span>
                            Canopy
                        </span>

                    </div>


                    <div className="map-status-item">

                        <span className="map-status-dot water" />

                        <span>
                            Water
                        </span>

                    </div>


                    <div className="map-status-item">

                        <span className="map-status-dot urban" />

                        <span>
                            Urban
                        </span>

                    </div>

                </div>


                <div className="map-status-right">

                    <Activity
                        size={13}
                        strokeWidth={2}
                    />

                    <span>
                        Spatial layer active
                    </span>

                </div>

            </div>

        </div>

    );

}