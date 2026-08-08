import "./AICommandCenter.css";

import {
    Cpu,
    Database,
    BrainCircuit,
    TimerReset,
    Activity,
    CheckCircle2,
    HardDrive,
    Layers3,
    Wifi
} from "lucide-react";

import { useEffect, useState } from "react";

import {
    getStatus,
    getDashboard
} from "../../services/api";


export default function AICommandCenter(){


    const [stats,setStats] = useState({});


    useEffect(()=>{


        async function load(){


            try{


                const dashboard =
                    await getDashboard();


                const status =
                    await getStatus();



                setStats({

                    backend:
                    status.status === 200
                    ? "Connected"
                    : "Offline",


                    wards:
                    dashboard.data.summary?.total_wards || "--"

                });


            }

            catch(err){

                console.log(err);

            }


        }


        load();


    },[]);



    const cards=[


        {
            title:"Model",
            value:"SegFormer-B0",
            icon:<BrainCircuit/>
        },


        {
            title:"Backend",
            value:stats.backend || "Checking",
            icon:<Wifi/>
        },


        {
            title:"AI Status",
            value:"Ready",
            icon:<CheckCircle2/>
        },


        {
            title:"Tiles",
            value:"440",
            icon:<Layers3/>
        },


        {
            title:"Inference",
            value:"Completed",
            icon:<TimerReset/>
        },


        {
            title:"Confidence",
            value:"94%",
            icon:<Activity/>
        },


        {
            title:"Dataset",
            value:"13 Bands",
            icon:<Database/>
        },


        {
            title:"Device",
            value:"CUDA / CPU",
            icon:<Cpu/>
        },


        {
            title:"Output",
            value:"GeoTIFF",
            icon:<HardDrive/>
        }


    ];



    return(


        <div className="command-center">


            <div className="command-header">


                <h2>
                    AI Command Center
                </h2>


                <p>
                    Live AI Pipeline Information
                </p>


            </div>



            <div className="command-grid">


            {

                cards.map((card,index)=>(


                    <div
                        className="command-item"
                        key={index}
                    >


                        <div className="command-icon">

                            {card.icon}

                        </div>


                        <div>

                            <span>
                                {card.title}
                            </span>


                            <h3>
                                {card.value}
                            </h3>

                        </div>


                    </div>


                ))

            }


            </div>


        </div>


    );

}