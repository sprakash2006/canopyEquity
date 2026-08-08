import "./ProgressTracker.css";

import {
    CheckCircle2,
    Circle,
    Loader2,
    AlertCircle
} from "lucide-react";

import {
    useEffect,
    useState
} from "react";

import {
    getPipelineStatus
} from "../../services/api";


export default function ProgressTracker(){


    const [pipeline,setPipeline] = useState({});

    const [loading,setLoading] = useState(true);

    const [error,setError] = useState(false);



    const steps=[

        {
            key:"upload",
            name:"Satellite Upload"
        },

        {
            key:"ai_engine",
            name:"AI Segmentation Engine"
        },

        {
            key:"impact_engine",
            name:"Impact Analysis Engine"
        },

        {
            key:"ward_engine",
            name:"Ward Ranking Engine"
        },

        {
            key:"recommendation_engine",
            name:"Recommendation Engine"
        },

        {
            key:"export",
            name:"Export Results"
        }

    ];



    useEffect(()=>{


        const loadStatus = async()=>{


            try{


                const response =
                    await getPipelineStatus();


                setPipeline(
                    response.data.pipeline || {}
                );


                setError(false);


            }


            catch(err){


                console.error(
                    "Pipeline Error:",
                    err
                );


                setError(true);

            }


            finally{


                setLoading(false);

            }

        };



        loadStatus();



        const interval=setInterval(

            loadStatus,

            5000

        );



        return ()=>clearInterval(interval);



    },[]);





    const getStepStatus=(key)=>{


        return pipeline[key]?.status || "pending";

    };




    const formatStatus=(status)=>{


        if(status==="completed")
            return "Completed";


        if(status==="running")
            return "Running";


        return "Waiting";


    };





    return (

        <div className="progress-card">


            <h2>
                AI Pipeline
            </h2>


            <p>
                Urban canopy intelligence workflow
            </p>



            {
                error &&

                <div className="pipeline-error">

                    <AlertCircle size={18}/>

                    Backend unavailable

                </div>

            }



            <div className="progress-list">


            {

                steps.map(step=>{


                    const status =
                        getStepStatus(step.key);



                    const completed =
                        status==="completed";


                    const active =
                        status==="running";



                    return (

                        <div

                            key={step.key}

                            className={

                                `progress-item

                                ${completed?"completed":""}

                                ${active?"active":""}`

                            }

                        >



                            {
                                completed &&

                                <CheckCircle2 size={22}/>

                            }



                            {
                                active &&

                                <Loader2

                                    size={22}

                                    className="spin"

                                />

                            }



                            {
                                !completed &&
                                !active &&

                                <Circle size={22}/>

                            }




                            <span>

                                {step.name}

                            </span>



                            <strong>

                                {

                                loading

                                ?

                                "Checking..."

                                :

                                formatStatus(status)

                                }

                            </strong>


                        </div>

                    );


                })

            }


            </div>


        </div>

    );

}