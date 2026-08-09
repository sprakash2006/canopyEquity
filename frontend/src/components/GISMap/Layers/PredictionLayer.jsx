import {
    useEffect
} from "react";


import {
    useMap
} from "react-leaflet";


import parseGeoraster from "georaster";

import GeoRasterLayer from "georaster-layer-for-leaflet";

import proj4 from "proj4";


window.proj4 = proj4;



export default function PredictionLayer(){


    const map = useMap();



    useEffect(()=>{


        console.log(
            "Prediction Layer Mounted"
        );


        let rasterLayer = null;



        const loadPrediction = async()=>{


            try{


                console.log(
                    "Loading canopy_prediction_web.tif"
                );



                const response = await fetch(

                    "http://127.0.0.1:8000/outputs/canopy_prediction_web.tif"

                );



                if(!response.ok){

                    throw new Error(
                        "TIFF file not found"
                    );

                }



                const buffer =
                    await response.arrayBuffer();



                const georaster =
                    await parseGeoraster(
                        buffer
                    );



                console.log(
                    "GeoRaster Loaded",
                    georaster
                );





                rasterLayer = new GeoRasterLayer({


                    georaster,


                    opacity:0.75,


                    resolution:256,


                    debugLevel:0,


                    noDataValue:0,



                    pixelValuesToColorFn:(values)=>{


                        if(
                            !values ||
                            values.length===0
                        ){

                            return null;

                        }



                        const value =
                            Number(values[0]);



                        if(
                            !value ||
                            isNaN(value)
                        ){

                            return null;

                        }




                        if(value===1){

                            return "#15803d";

                        }



                        if(value===2){

                            return "#84cc16";

                        }



                        if(value===3){

                            return "#2563eb";

                        }




                        if(value>0.7){

                            return "#15803d";

                        }


                        if(value>0.3){

                            return "#84cc16";

                        }



                        return null;


                    }


                });







                // Wait for leaflet completely ready

                setTimeout(()=>{


                    if(!map){

                        console.log(
                            "Map not available"
                        );

                        return;

                    }



                    try{


                        // IMPORTANT FIX

                        map.whenReady(()=>{


                            if(!map._container){

                                console.log(
                                    "Leaflet container missing"
                                );

                                return;

                            }




                            rasterLayer.addTo(map);



                            console.log(
                                "Prediction Layer Added"
                            );




                            /* Do NOT fitBounds here — the raster's
                               bounds may not match the current AOI
                               (Delhi) and would jerk the whole map
                               away.                                */



                        });



                    }


                    catch(error){


                        console.error(
                            "Raster Add Error",
                            error
                        );


                    }



                },1000);




            }


            catch(error){


                console.error(
                    "Prediction Layer Error",
                    error
                );


            }



        };



        loadPrediction();




        return ()=>{


            console.log(
                "Prediction Layer Removed"
            );



            if(
                rasterLayer &&
                map &&
                map.hasLayer(rasterLayer)
            ){

                map.removeLayer(
                    rasterLayer
                );

            }


        };



    },[map]);




    return null;


}