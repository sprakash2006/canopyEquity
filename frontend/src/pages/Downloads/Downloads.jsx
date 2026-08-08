import "./Downloads.css";

import {
    Download,
    FileText,
    Database,
    Map,
    Image,
    FileSpreadsheet,
    Loader2,
    CheckCircle
} from "lucide-react";


import {
    useState
} from "react";



const API_URL = "http://localhost:8000";




const files = [


    {
        name:"AI Canopy Prediction",
        file:"canopy_prediction_web.tif",
        type:"GeoTIFF",
        icon:<Image/>
    },


    {
        name:"Ward Rankings GeoJSON",
        file:"ward_rankings_web.geojson",
        type:"GIS Data",
        icon:<Map/>
    },


    {
        name:"Dashboard Data",
        file:"dashboard_data.json",
        type:"JSON",
        icon:<Database/>
    },


    {
        name:"Top Recommendations",
        file:"top10_recommendations.json",
        type:"AI Output",
        icon:<FileText/>
    },


    {
        name:"Final Recommendations",
        file:"final_recommendations.csv",
        type:"CSV",
        icon:<FileSpreadsheet/>
    },


    {
        name:"Optimized Plantation Plan",
        file:"optimized_plan.csv",
        type:"CSV",
        icon:<FileSpreadsheet/>
    },


    {
        name:"AI Evaluation Report",
        file:"CanopyAI_Evaluation_Report.pdf",
        type:"PDF Report",
        icon:<FileText/>
    }


];







export default function Downloads(){


    const [downloading,setDownloading] = useState("");




    const downloadFile = async(file)=>{


        try{


            setDownloading(file);



            const url =
            `${API_URL}/outputs/${file}`;



            const response =
            await fetch(url);



            if(!response.ok){

                throw new Error(
                    "File not found"
                );

            }



            const blob =
            await response.blob();



            const link =
            document.createElement("a");



            link.href =
            window.URL.createObjectURL(blob);



            link.download =
            file;



            document.body.appendChild(link);



            link.click();



            link.remove();



        }


        catch(error){


            console.error(
                "Download Error",
                error
            );


            alert(
                "File not available yet"
            );


        }


        finally{


            setDownloading("");

        }



    };







    return(



    <div className="downloads">






        <div className="downloads-header">


            <h1>
                Download AI Results
            </h1>



            <p>
                Export generated GIS, AI and recommendation outputs
            </p>



        </div>








        <div className="download-grid">



        {

            files.map((item,index)=>(



                <div

                className="download-card"

                key={index}

                >





                    <div className="file-info">



                        <div className="file-icon">

                            {item.icon}

                        </div>




                        <div>


                            <h3>

                                {item.name}

                            </h3>



                            <span>

                                {item.type}

                            </span>



                        </div>



                    </div>









                    <button


                    onClick={()=>downloadFile(item.file)}



                    disabled={
                        downloading===item.file
                    }



                    >




                    {

                    downloading===item.file ?


                    <>

                    <Loader2
                        size={18}
                        className="spin"
                    />

                    Downloading

                    </>



                    :


                    <>

                    <Download
                        size={18}
                    />

                    Download

                    </>


                    }





                    </button>






                </div>



            ))


        }



        </div>







        <div className="download-status">


            <CheckCircle size={18}/>


            All AI generated outputs are ready


        </div>





    </div>



    );

}