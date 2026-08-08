import "./Analysis.css";

import {
    BrainCircuit,
    Satellite,
    TreePine,
    Layers,
    Target,
    Activity
} from "lucide-react";


export default function Analysis(){


    const cards = [

        {
            title:"AI Model",
            value:"SegFormer-B0",
            icon:<BrainCircuit/>
        },

        {
            title:"Input Dataset",
            value:"Satellite 13 Bands",
            icon:<Satellite/>
        },

        {
            title:"Segmentation",
            value:"Completed",
            icon:<Layers/>
        },

        {
            title:"Canopy Detection",
            value:"Active",
            icon:<TreePine/>
        },

        {
            title:"Impact Engine",
            value:"Running",
            icon:<Target/>
        },

        {
            title:"AI Status",
            value:"Ready",
            icon:<Activity/>
        }

    ];



    const outputs=[

        "Canopy Prediction GeoTIFF",

        "Canopy Deficit Map",

        "Plantability Map",

        "Impact Score Raster",

        "Ward Priority Analysis",

        "Recommendation Engine"

    ];



    return (

        <div className="analysis-page">


            <div className="analysis-header">


                <h1>
                    AI Analysis
                </h1>


                <p>
                    Satellite based urban canopy intelligence pipeline
                </p>


            </div>



            <div className="analysis-grid">


            {
                cards.map((item,index)=>(

                    <div
                        className="analysis-card"
                        key={index}
                    >

                        <div className="analysis-icon">

                            {item.icon}

                        </div>


                        <div>

                            <span>
                                {item.title}
                            </span>


                            <h2>
                                {item.value}
                            </h2>

                        </div>


                    </div>


                ))

            }


            </div>




            <div className="pipeline">


                <h2>
                    AI Pipeline
                </h2>



                <div className="pipeline-flow">


                    <div>
                        Satellite Image
                    </div>


                    <div>
                        ↓
                    </div>


                    <div>
                        AI Segmentation
                    </div>


                    <div>
                        ↓
                    </div>


                    <div>
                        Canopy Mask
                    </div>


                    <div>
                        ↓
                    </div>


                    <div>
                        Impact Analysis
                    </div>


                    <div>
                        ↓
                    </div>


                    <div>
                        Plantation Recommendation
                    </div>


                </div>


            </div>




            <div className="outputs">


                <h2>
                    Generated Outputs
                </h2>



                <div className="output-grid">


                {
                    outputs.map((item,index)=>(

                        <div
                            className="output-card"
                            key={index}
                        >

                            <Layers size={22}/>

                            {item}


                        </div>

                    ))
                }


                </div>


            </div>



        </div>

    );

}