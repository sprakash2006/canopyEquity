import { GeoJSON } from "react-leaflet";
import { useEffect, useState, useRef } from "react";

export default function WardLayer({

    onWardSelect

}) {

    const [geoData, setGeoData] = useState(null);

    const selectedLayer = useRef(null);

    // ==========================================================
    // LOAD WEB GEOJSON
    // ==========================================================

    useEffect(() => {

        fetch("http://127.0.0.1:8000/outputs/ward_rankings_web.geojson")

            .then((res) => {

                if (!res.ok) {

                    throw new Error("Failed to load GeoJSON");

                }

                return res.json();

            })

            .then((data) => {

                console.log("Ward GeoJSON Loaded");

                console.log(data);

                setGeoData(data);

            })

            .catch((err) => {

                console.error(err);

            });

    }, []);

    // ==========================================================
    // PRIORITY COLOR
    // ==========================================================

    const getColor = (priority) => {

        if (!priority) return "#717973";

        switch ((priority || "").toUpperCase()) {

            case "VERY HIGH":
                return "#ba1a1a";

            case "HIGH":
                return "#f48c24";

            case "MEDIUM":
                return "#eab552";

            case "LOW":
                return "#3e6752";

            case "VERY LOW":
                return "#7fa38f";

            default:
                return "#717973";

        }

    };

    // ==========================================================
    // DEFAULT STYLE
    // ==========================================================

    const style = (feature) => {

        const p = feature.properties;

        return {

            color: "#ffffff",

            weight: 1.5,

            fillColor: getColor(

                p.Priority ||

                p.priority

            ),

            fillOpacity: 0.65

        };

    };

    // ==========================================================
    // FEATURE EVENTS
    // ==========================================================

    const onEachFeature = (feature, layer) => {

        const p = feature.properties;

        layer.bindPopup(`

            <div style="min-width:240px">

                <h3>

                    ${

                        p.ward_name ||

                        p.Ward_Name ||

                        p.WARD_NAME ||

                        p.NAME ||

                        "Unknown Ward"

                    }

                </h3>

                <hr/>

                <b>Priority</b><br/>

                ${

                    p.Priority ||

                    p.priority ||

                    "-"

                }

                <br/><br/>

                <b>Impact Score</b><br/>

                ${

                    Number(

                        p.Composite_Score ??

                        p.score ??

                        0

                    ).toFixed(2)

                }

            </div>

        `);

        layer.on({

            mouseover(e) {

                if (selectedLayer.current !== e.target) {

                    e.target.setStyle({

                        weight: 3,

                        fillOpacity: 0.9

                    });

                }

            },

            mouseout(e) {

                if (selectedLayer.current !== e.target) {

                    e.target.setStyle({

                        weight: 1.5,

                        fillOpacity: 0.65

                    });

                }

            },

            click(e) {

                // --------------------------------------
                // Reset previous selection
                // --------------------------------------

                if (selectedLayer.current) {

                    selectedLayer.current.setStyle({

                        weight: 1.5,

                        fillOpacity: 0.65,

                        color: "#ffffff"

                    });

                }

                // --------------------------------------
                // Highlight current ward
                // --------------------------------------

                selectedLayer.current = e.target;

                e.target.setStyle({

                    weight: 5,

                    color: "#00ffff",

                    fillOpacity: 1

                });

                // --------------------------------------
                // Zoom to ward
                // --------------------------------------

                e.target._map.fitBounds(

                    e.target.getBounds(),

                    {

                        padding: [40, 40]

                    }

                );

                // --------------------------------------
                // Update Right Panel
                // --------------------------------------

                if (onWardSelect) {

                    onWardSelect(p);

                }

            }

        });

    };

    if (!geoData) return null;

    return (

        <GeoJSON

            data={geoData}

            style={style}

            onEachFeature={onEachFeature}

        />

    );

}