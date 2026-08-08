import "./Recommendations.css";

import {
    useEffect,
    useState
} from "react";


import {
    TreePine,
    IndianRupee,
    Thermometer,
    Target,
    Leaf
} from "lucide-react";


import {
    getRecommendations
} from "../../services/api";



export default function Recommendation(){


    const [recommendations,setRecommendations] = useState([]);

    const [loading,setLoading] = useState(true);



    useEffect(()=>{


        const fetchRecommendations = async()=>{


            try{


                const response = await getRecommendations();


                console.log(
                    "RECOMMENDATION API RESPONSE",
                    response.data
                );


                setRecommendations(

                    response.data.recommendations || []

                );


            }
            catch(error){


                console.error(
                    "Recommendation API Error",
                    error
                );


                setRecommendations([]);


            }
            finally{


                setLoading(false);


            }


        };


        fetchRecommendations();


    },[]);




    const formatMoney=(value)=>{


        if(
            value === null ||
            value === undefined ||
            value === ""
        ){

            return "N/A";

        }


        return Number(value)
        .toLocaleString("en-IN");


    };





    return (

        <div className="recommendations-page">



            <div className="page-header">


                <h1>
                    🌱 AI Planting Recommendations
                </h1>


                <p>
                    Optimized locations for urban tree plantation
                </p>


            </div>





            {

            loading ?


            <h2>
                Loading AI Recommendations...
            </h2>


            :



            recommendations.length === 0 ?


            <h2>
                No recommendations found
            </h2>


            :



            <div className="recommendation-grid">



            {


            recommendations
            .slice(0,10)
            .map((ward,index)=>(


                <div

                className="recommendation-card"

                key={index}

                >




                    <div className="recommendation-title">


                        <TreePine size={28}/>


                        <h2>

                        {
                            ward.ward_name ||
                            `Ward ${index+1}`
                        }

                        </h2>


                    </div>





                    <span className="priority">


                    {
                        ward.Priority ||
                        "VERY HIGH"
                    }


                    </span>






                    <div className="stats">



                        <p>

                        <Leaf size={16}/>

                        🌳 Trees Suggested:


                        <b>

                        {
                            ward.Recommended_Trees ??
                            "N/A"
                        }

                        </b>


                        </p>






                        <p>

                        <IndianRupee size={16}/>

                        💰 Budget:


                        <b>

                        ₹
                        {
                            formatMoney(
                                ward.Estimated_Budget
                            )
                        }

                        </b>


                        </p>






                        <p>

                        <Thermometer size={16}/>

                        ❄ Cooling Impact:


                        <b>

                        {
                            ward.Estimated_Cooling_C ??
                            "N/A"
                        }

                        °C

                        </b>


                        </p>






                        <p>


                        🌱 Carbon Capture:


                        <b>

                        {
                            ward.Annual_CO2_Tons ??
                            "N/A"
                        }


                        Tons/year

                        </b>


                        </p>






                        <p>

                        <Target size={16}/>


                        ⭐ Impact Score:


                        <b>


                        {

                        Number(

                            ward.Final_Score ??
                            ward.Composite_Score ??
                            0

                        )
                        .toFixed(2)


                        }


                        </b>


                        </p>



                    </div>



                </div>



            ))


            }



            </div>


            }



        </div>


    );

}