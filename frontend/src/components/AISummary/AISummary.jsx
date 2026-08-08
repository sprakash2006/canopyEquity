import "./AISummary.css";

import {
    Cpu,
    CheckCircle2,
    TimerReset,
    Image,
    Grid2X2,
    BrainCircuit,
    Activity
} from "lucide-react";

export default function AISummary(){

    const items=[

        {
            icon:<Cpu size={22}/>,
            label:"Model",
            value:"SegFormer-B0"
        },

        {
            icon:<CheckCircle2 size={22}/>,
            label:"Status",
            value:"Ready"
        },

        {
            icon:<BrainCircuit size={22}/>,
            label:"Confidence",
            value:"--"
        },

        {
            icon:<TimerReset size={22}/>,
            label:"Inference Time",
            value:"--"
        },

        {
            icon:<Grid2X2 size={22}/>,
            label:"Tiles",
            value:"440"
        },

        {
            icon:<Image size={22}/>,
            label:"Image Size",
            value:"5067 × 5401"
        }

    ];

    return(

        <div className="ai-summary">

            <div className="summary-header">

                <Activity size={22}/>

                <div>

                    <h2>

                        AI Engine

                    </h2>

                    <p>

                        Live Model Information

                    </p>

                </div>

            </div>

            <div className="summary-grid">

                {

                    items.map((item,index)=>(

                        <div
                            className="summary-item"
                            key={index}
                        >

                            <div className="summary-icon">

                                {item.icon}

                            </div>

                            <div>

                                <span>

                                    {item.label}

                                </span>

                                <h3>

                                    {item.value}

                                </h3>

                            </div>

                        </div>

                    ))

                }

            </div>

        </div>

    )

}