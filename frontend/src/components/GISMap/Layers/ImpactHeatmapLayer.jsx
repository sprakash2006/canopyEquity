import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";


/* Pixel-level impact heatmap.

   The raster is pre-coloured and reprojected to WGS84 on the
   server (see outputs/impact_score_web.png).  We just drop it
   on the map as an ImageOverlay so the browser doesn't have to
   parse 27 MB of GeoTIFF or reproject millions of cells.        */


export default function ImpactHeatmapLayer({
    opacity = 0.75
}) {

    const map = useMap();
    const layerRef = useRef(null);


    useEffect(() => {

        if (layerRef.current) {
            layerRef.current.setOpacity(opacity);
        }

    }, [opacity]);


    useEffect(() => {

        if (!map) return;

        let disposed = false;

        const load = async () => {

            try {

                const boundsRes = await fetch(
                    "http://127.0.0.1:8000/outputs/impact_score_web.bounds.json?v=6"
                );

                if (!boundsRes.ok) {
                    throw new Error("bounds json missing");
                }

                const b = await boundsRes.json();

                if (disposed) return;

                const layer = L.imageOverlay(
                    "http://127.0.0.1:8000/outputs/impact_score_web.png?v=6",
                    [
                        [b.south, b.west],
                        [b.north, b.east]
                    ],
                    {
                        opacity,
                        interactive: false,
                        /* Nearest-neighbour scaling keeps 10 m
                           cells crisp instead of blurring them
                           into ward-scale washes.                */
                        className: "impact-heatmap-image"
                    }
                );

                layerRef.current = layer;

                layer.addTo(map);

                /* Do NOT auto-fit — the parent MapContainer is
                   already centered on Delhi. fitBounds would
                   jerk the user's current view.                  */

            } catch (err) {
                console.error("Impact Heatmap Error", err);
            }
        };

        load();

        return () => {

            disposed = true;

            const layer = layerRef.current;

            if (layer) {
                try {
                    map.removeLayer(layer);
                } catch (_) { /* map torn down */ }
                layerRef.current = null;
            }
        };

    }, [map]);


    return null;
}
