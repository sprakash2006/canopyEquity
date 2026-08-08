import "./MapViewer.css";

import GISMap from "../../components/GISMap/GISMap";

export default function MapViewer() {

    return (

        <div className="mapviewer-page">

            <div className="mapviewer-header">

                <h1>Canopy AI GIS Viewer</h1>

                <p>

                    Interactive Urban Tree Canopy Analysis

                </p>

            </div>

            <div className="mapviewer-body">

                <div className="map-section">

                    <GISMap />

                </div>

            </div>

        </div>

    );

}