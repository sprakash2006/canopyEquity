import { 
    useEffect, 
    useState 
} from "react";

import "./Recommendations.css";


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





export default function Recommendations(){


    const [recommendations,setRecommendations] = useState([]);

    const [loading,setLoading] = useState(true);





    useEffect(()=>{


        async function loadRecommendations(){


            try{


                const response = 
                    await getRecommendations();



                console.log(
                    "RECOMMENDATIONS RESPONSE",
                    response.data
                );



                setRecommendations(

                    response.data.recommendations || []

                );


            }


            catch(error){


                console.error(
                    "Recommendation Error",
                    error
                );


                setRecommendations([]);


            }



            finally{


                setLoading(false);


            }


        }



        loadRecommendations();



    },[]);








    const formatMoney=(value)=>{


        if(
            value === null ||
            value === undefined
        ){

            return "N/A";

        }


        return Number(value)
        .toLocaleString("en-IN");


    };









    return (


        <div className="recommendation-page">






            <div className="recommendation-header">


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



            <div className="recommendation-grid">







            {

            recommendations
            .slice(0,10)
            .map((item,index)=>(



                <div

                className="recommendation-card"

                key={index}

                >







                    <div className="recommendation-title">



                        <TreePine size={28}/>



                        <h2>

                        {
                            item.ward_name ||

                            `Ward ${index+1}`

                        }

                        </h2>


                    </div>









                    <div className="recommendation-data">







                        <p>

                        <Target size={16}/>

                        Priority:


                        <b>

                        {
                            item.Priority ||

                            "N/A"

                        }

                        </b>


                        </p>









                        <p>

                        <Leaf size={16}/>

                        Trees Suggested:


                        <b>

                        {

                        item.Recommended_Trees ??

                        "N/A"

                        }


                        </b>


                        </p>









                        <p>

                        <IndianRupee size={16}/>

                        Budget:


                        <b>

                        ₹
                        {

                        formatMoney(

                        item.Estimated_Budget

                        )

                        }


                        </b>


                        </p>









                        <p>

                        <Thermometer size={16}/>

                        Cooling Impact:


                        <b>


                        {

                        item.Estimated_Cooling_C ??

                        "N/A"

                        }


                        °C


                        </b>


                        </p>









                        <p>

                        🌱 Carbon Capture:


                        <b>


                        {

                        item.Annual_CO2_Tons ??

                        "N/A"

                        }


                        Tons/year


                        </b>


                        </p>









                        <p>

                        ⭐ Impact Score:


                        <b>


                        {

                        Number(

                        item.Final_Score ??

                        item.Composite_Score ??

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