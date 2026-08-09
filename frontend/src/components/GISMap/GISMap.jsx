import "./GISMap.css";
import "leaflet/dist/leaflet.css";

import {
    MapContainer,
    TileLayer,
    LayersControl,
    ZoomControl,
    ScaleControl,
    useMap
} from "react-leaflet";

import { useEffect } from "react";

import PredictionLayer from "./Layers/PredictionLayer";
import ImpactHeatmapLayer from "./Layers/ImpactHeatmapLayer";
import Legend from "./Legend";

const {
    BaseLayer,
    Overlay
} = LayersControl;


// ============================================================
// MAP SIZE FIX
// Forces Leaflet to recalculate its actual container size.
// Important when the map is inside a dashboard/grid.
// ============================================================

function MapResizeHandler() {

    const map = useMap();

    useEffect(() => {

        const resizeMap = () => {

            setTimeout(() => {

                map.invalidateSize({
                    animate: false
                });

            }, 100);

        };


        // Initial resize
        resizeMap();


        // Browser resize
        window.addEventListener(
            "resize",
            resizeMap
        );


        // Observe parent/container size changes
        const container =
            map.getContainer();

        const resizeObserver =
            new ResizeObserver(() => {

                map.invalidateSize({
                    animate: false
                });

            });


        resizeObserver.observe(
            container
        );


        return () => {

            window.removeEventListener(
                "resize",
                resizeMap
            );

            resizeObserver.disconnect();

        };

    }, [map]);


    return null;
}


// ============================================================
// GIS MAP
// ============================================================

export default function GISMap() {

    return (

        <div className="gis-map-container">


            <MapContainer

                center={[
                    28.6139,
                    77.2090
                ]}

                zoom={11}

                zoomControl={false}

                scrollWheelZoom={true}

                preferCanvas={true}

                className="canopy-leaflet-map"

                style={{
                    width: "100%",
                    height: "100%",
                    minHeight: "0"
                }}

            >


                {/* =================================================
                    FORCE MAP RESIZE
                ================================================= */}

                <MapResizeHandler />


                {/* =================================================
                    MAP CONTROLS
                ================================================= */}

                <ZoomControl
                    position="bottomright"
                />


                <ScaleControl
                    position="bottomleft"
                />


                {/* =================================================
                    MAP LAYERS
                ================================================= */}

                <LayersControl
                    position="topright"
                >


                    {/* =============================================
                        STREET MAP
                    ============================================= */}

                    <BaseLayer
                        checked
                        name="Street Map"
                    >

                        <TileLayer

                            attribution="© OpenStreetMap"

                            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"

                        />

                    </BaseLayer>


                    {/* =============================================
                        SATELLITE
                    ============================================= */}

                    <BaseLayer
                        name="Satellite"
                    >

                        <TileLayer

                            attribution="Google Satellite"

                            url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

                        />

                    </BaseLayer>


                    {/* =============================================
                        IMPACT PRIORITY
                    ============================================= */}

                    <Overlay
                        checked
                        name="Impact Priority"
                    >

                        <ImpactHeatmapLayer />

                    </Overlay>


                    {/* =============================================
                        AI PIXEL SEGMENTATION
                    ============================================= */}

                    <Overlay
                        checked
                        name="AI Pixel Segmentation"
                    >

                        <PredictionLayer />

                    </Overlay>


                </LayersControl>


                {/* =================================================
                    LEGEND
                ================================================= */}

                <Legend />


            </MapContainer>


        </div>

    );

}