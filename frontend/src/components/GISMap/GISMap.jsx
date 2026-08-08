import "./GISMap.css";

import "leaflet/dist/leaflet.css";

import {
    MapContainer,
    TileLayer,
    LayersControl,
    ZoomControl,
    ScaleControl
} from "react-leaflet";


import WardLayer from "./Layers/WardLayer";
import PredictionLayer from "./Layers/PredictionLayer";
import Legend from "./Legend";



const {
    BaseLayer,
    Overlay
} = LayersControl;




export default function GISMap(){


    return (

        <div className="gis-map-container">


            <MapContainer


                center={[28.6139,77.2090]}


                zoom={11}


                zoomControl={false}


                scrollWheelZoom={true}


                preferCanvas={true}



            >



                <ZoomControl

                    position="bottomright"

                />



                <ScaleControl

                    position="bottomleft"

                />





                <LayersControl

                    position="topright"

                >





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







                    <Overlay

                        checked

                        name="Ward Priority"

                    >


                        <WardLayer/>


                    </Overlay>







                    <Overlay

                        checked

                        name="AI Canopy Prediction"

                    >


                        <PredictionLayer/>


                    </Overlay>





                </LayersControl>





                <Legend/>





            </MapContainer>



        </div>


    );

}