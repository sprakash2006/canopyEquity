import "./Ranking.css";

import {
    useEffect,
    useState
} from "react";


import {
    getWardRankings
} from "../../services/api";



export default function Ranking(){


    const [wards,setWards] = useState([]);

    const [loading,setLoading] = useState(true);




useEffect(()=>{

    async function loadRanking(){

        try{

            const response = await getWardRankings();

            console.log(
                "WARD RANKING RESPONSE",
                response.data
            );


            let data = response.data;



            // CASE 1: GeoJSON directly
            if(
                data.type === "FeatureCollection" &&
                Array.isArray(data.features)
            ){

                data = data.features.map(
                    feature => feature.properties
                );

            }


            // CASE 2: wrapped GeoJSON
            else if(
                data.data &&
                data.data.type === "FeatureCollection"
            ){

                data = data.data.features.map(
                    feature => feature.properties
                );

            }


            // CASE 3: normal array
            else if(
                Array.isArray(data)
            ){

                data = data;

            }


            // CASE 4: backend ranking key
            else if(
                Array.isArray(data.rankings)
            ){

                data = data.rankings;

            }


            else if(
                Array.isArray(data.ward_rankings)
            ){

                data = data.ward_rankings;

            }


            else{

                console.log(
                    "UNKNOWN FORMAT",
                    data
                );

                data=[];

            }



            console.log(
                "FINAL RANKING ARRAY",
                data
            );


            setWards(data);


        }

        catch(error){

            console.error(
                "Ranking Error",
                error
            );

            setWards([]);

        }

        finally{

            setLoading(false);

        }

    }


    loadRanking();


},[]);







    return (

        <div className="ranking-page">






            <div className="page-header">


                <h1>
                    Ward Ranking
                </h1>


                <p>
                    AI generated urban canopy priority ranking
                </p>


            </div>








            {


            loading ?


            <h2>
                Loading rankings...
            </h2>



            :



            <div className="ranking-table">







                <div className="table-header">


                    <span>
                        Rank
                    </span>


                    <span>
                        Ward
                    </span>


                    <span>
                        Score
                    </span>


                    <span>
                        Priority
                    </span>


                </div>










                {


                [...wards]

                .sort(

                    (a,b)=>


                    Number(

                        a.Final_Rank ??
                        a.final_rank ??
                        a.Rank ??
                        a.rank ??
                        999

                    )

                    -

                    Number(

                        b.Final_Rank ??
                        b.final_rank ??
                        b.Rank ??
                        b.rank ??
                        999

                    )


                )


                .slice(0,10)


                .map((ward,index)=>(




                    <div

                    className="table-row"

                    key={index}

                    >






                        <span>


                            #

                            {

                            ward.Final_Rank ??

                            ward.final_rank ??

                            ward.Rank ??

                            ward.rank ??

                            index+1

                            }


                        </span>







                        <span>


                        {

                        ward.ward_name ??

                        ward.WARD_NAME ??

                        ward.name ??

                        ward.Name ??

                        "Unknown Ward"

                        }


                        </span>








                        <span>


                        {

                        Number(

                            ward.Composite_Score ??

                            ward.Final_Score ??

                            ward.final_score ??

                            ward.score ??

                            0

                        )
                        .toFixed(2)


                        }


                        </span>









                        <span

                        className="priority-badge"

                        >



                        {

                        ward.Priority ??

                        ward.priority ??

                        "N/A"


                        }


                        </span>






                    </div>





                ))



                }








            </div>




            }





        </div>


    );

}