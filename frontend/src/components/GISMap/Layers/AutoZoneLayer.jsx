import { useEffect, useState } from "react";
import { GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";


/* Same red -> green ramp used by the pixel heatmap */
const STOPS = [
    { pos: 0,   rgb: [62, 103, 82] },
    { pos: 25,  rgb: [127, 163, 143] },
    { pos: 50,  rgb: [234, 181, 82] },
    { pos: 75,  rgb: [244, 140, 36] },
    { pos: 100, rgb: [186, 26, 26] }
];


function scoreToColor(value) {

    if (value <= STOPS[0].pos) {
        return `rgb(${STOPS[0].rgb.join(",")})`;
    }
    if (value >= STOPS[STOPS.length - 1].pos) {
        return `rgb(${STOPS[STOPS.length - 1].rgb.join(",")})`;
    }

    for (let i = 0; i < STOPS.length - 1; i++) {
        const a = STOPS[i];
        const b = STOPS[i + 1];
        if (value <= b.pos) {
            const t = (value - a.pos) / (b.pos - a.pos);
            const r = Math.round(a.rgb[0] + t * (b.rgb[0] - a.rgb[0]));
            const g = Math.round(a.rgb[1] + t * (b.rgb[1] - a.rgb[1]));
            const bl = Math.round(a.rgb[2] + t * (b.rgb[2] - a.rgb[2]));
            return `rgb(${r},${g},${bl})`;
        }
    }

    return "#888";
}


export default function AutoZoneLayer({
    onZoneSelect,
    selectedZoneId
}) {

    const [data, setData] = useState(null);
    const map = useMap();


    useEffect(() => {

        let cancelled = false;

        const load = async () => {

            try {

                const res = await fetch(
                    "http://127.0.0.1:8000/outputs/auto_zones.geojson"
                );

                if (!res.ok) throw new Error("auto_zones.geojson not found");

                const geojson = await res.json();

                if (!cancelled) {
                    setData(geojson);
                    /* Note: map centering is handled by AutoFitToData
                       in GISMap so it works even when this layer is off. */
                }

            } catch (err) {
                console.error("AutoZoneLayer load error:", err);
            }
        };

        load();

        return () => { cancelled = true; };

    }, [map]);


    if (!data) return null;


    const styleFeature = (feature) => {

        const score = Number(feature.properties?.impact_mean || 0);
        const isSelected =
            feature.properties?.zone_id === selectedZoneId;

        return {
            fillColor: scoreToColor(score),
            fillOpacity: isSelected ? 0.15 : 0.55,
            color: isSelected ? "#002d1c" : "#ffffff",
            weight: isSelected ? 3 : 1,
            opacity: 0.8
        };
    };


    const onEachFeature = (feature, layer) => {

        const p = feature.properties || {};

        layer.bindTooltip(
            `<strong>${p.zone_id || "Zone"}</strong><br/>` +
            `Impact: ${Number(p.impact_mean || 0).toFixed(1)}<br/>` +
            `Priority: ${p.priority || "-"}`,
            { direction: "top", sticky: true }
        );

        layer.on({
            click: () => {
                if (onZoneSelect) onZoneSelect(feature);
            }
        });
    };


    return (
        <GeoJSON
            key={selectedZoneId || "none"}
            data={data}
            style={styleFeature}
            onEachFeature={onEachFeature}
        />
    );
}
