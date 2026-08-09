import "./GISMap.css";

import "leaflet/dist/leaflet.css";

import {
    MapContainer,
    TileLayer,
    LayersControl,
    ZoomControl,
    ScaleControl
} from "react-leaflet";

import PredictionLayer from "./Layers/PredictionLayer";
import ImpactHeatmapLayer from "./Layers/ImpactHeatmapLayer";
import Legend from "./Legend";


const {
    BaseLayer,
    Overlay
} = LayersControl;


export default function GISMap() {

    return (

        <div className="gis-map-container">

            <MapContainer

                center={[28.6139, 77.2090]}

                zoom={11}

                zoomControl={false}

                scrollWheelZoom={true}

                preferCanvas={true}

            >

                {/* =====================================================
                    MAP CONTROLS
                ===================================================== */}

                <ZoomControl
                    position="bottomright"
                />

                <ScaleControl
                    position="bottomleft"
                />


                {/* =====================================================
                    MAP LAYERS
                ===================================================== */}

                <LayersControl
                    position="topright"
                >


                    {/* =================================================
                        BASE MAPS
                    ================================================= */}

                    <BaseLayer
                        checked
                        name="Street Map"
                    >

                        <TileLayer

                            attribution="© OpenStreetMap"

                            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"

                        />

                    </BaseLayer>


                    <BaseLayer
                        name="Satellite"
                    >

                        <TileLayer

                            attribution="Google Satellite"

                            url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

                        />

                    </BaseLayer>


                    {/* =================================================
                        ANALYTICS LAYERS
                    ================================================= */}

                    <Overlay
                        checked
                        name="Impact Priority"
                    >

                        <ImpactHeatmapLayer />

                    </Overlay>


                    <Overlay
                        checked
                        name="AI Pixel Segmentation"
                    >

                        <PredictionLayer />

                    </Overlay>


                </LayersControl>


                {/* =====================================================
                    MAP LEGEND
                ===================================================== */}

                <Legend />


            </MapContainer>

        </div>

    );

}