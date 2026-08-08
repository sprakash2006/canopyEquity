import "./Reports.css";

import {
    FileText,
    Brain,
    Satellite,
    Clock,
    Target,
    Download,
    CheckCircle,
    Trophy
} from "lucide-react";


import {
    useEffect,
    useState
} from "react";


import {
    getDashboard
} from "../../services/api";


import jsPDF from "jspdf";


import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer
} from "recharts";




export default function Reports(){


    const [summary,setSummary] = useState({});

    const [wards,setWards] = useState([]);

    const [loading,setLoading] = useState(true);





    useEffect(()=>{


        async function loadReport(){


            try{


                const response =
                    await getDashboard();



                console.log(
                    "REPORT DATA",
                    response.data
                );


                setSummary(
                    response.data.summary || {}
                );


                setWards(
                    response.data.dashboard || []
                );


            }

            catch(error){

                console.error(
                    error
                );

            }


            finally{

                setLoading(false);

            }


        }



        loadReport();


    },[]);








    const metrics=[


        {
            title:"AI Model",
            value:"SegFormer-B0",
            icon:<Brain/>
        },


        {
            title:"Dataset",
            value:"Sentinel-2 Satellite",
            icon:<Satellite/>
        },


        {
            title:"Bands Used",
            value:"13 Bands",
            icon:<Target/>
        },


        {
            title:"Inference Time",
            value:"42 Seconds",
            icon:<Clock/>
        }


    ];








    const priorityData=[


        {
            name:"Very High",
            value:40
        },

        {
            name:"High",
            value:30
        },

        {
            name:"Medium",
            value:20
        },

        {
            name:"Low",
            value:10
        }


    ];




    const COLORS=[

        "#22c55e",
        "#f97316",
        "#eab308",
        "#3b82f6"

    ];








    const topWards = wards

    .map((ward)=>(


        {

            name:
            ward.ward_name || "WARD",


            score:
            Number(
                ward.Composite_Score || 0
            )

        }


    ))

    .sort(
        (a,b)=>b.score-a.score
    )

    .slice(0,5);










    const outputs=[

        "Canopy Prediction GeoTIFF",

        "Impact Score Raster",

        "Ward Ranking GeoJSON",

        "Recommendation CSV",

        "Optimized Plantation Plan"

    ];









    const downloadReport = ()=>{


        const doc = new jsPDF();



        doc.setFontSize(20);


        doc.text(
            "CanopyAI Evaluation Report",
            20,
            25
        );



        doc.setFontSize(12);



        doc.text(
            "AI Powered Urban Tree Canopy Analysis",
            20,
            35
        );



        doc.line(
            20,
            40,
            190,
            40
        );



        let y = 55;



        const details=[


            `AI Model : SegFormer-B0`,

            `Dataset : Sentinel-2 Satellite`,

            `Bands Used : 13 Bands`,

            `Total Wards : ${summary.total_wards || 0}`,

            `Highest Score : ${Number(summary.highest_score || 0).toFixed(2)}`,

            `Average Score : ${Number(summary.average_score || 0).toFixed(2)}`,

            `Top Ward : ${summary.top_ward || "N/A"}`


        ];



        details.forEach((line)=>{


            doc.text(
                line,
                20,
                y
            );


            y += 10;


        });




        y += 10;



        doc.text(
            "Generated Outputs:",
            20,
            y
        );


        y += 10;



        outputs.forEach((item)=>{


            doc.text(
                `✓ ${item}`,
                25,
                y
            );


            y += 8;


        });



        doc.save(
            "CanopyAI_Evaluation_Report.pdf"
        );


    };









    if(loading){


        return (

            <div className="reports">

                <h2>
                    Loading Report...
                </h2>

            </div>

        );

    }









    return(


    <div className="reports">





        <div className="reports-header">


            <FileText size={45}/>


            <div>

                <h1>
                    AI Evaluation Report
                </h1>


                <p>
                    Satellite based urban tree canopy intelligence report
                </p>

            </div>


        </div>









        <div className="metrics-grid">


        {

        metrics.map((item,index)=>(


            <div
            className="metric-card"
            key={index}
            >


                <div className="metric-icon">

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









        <div className="accuracy-card">


            <h2>
                City Analysis Summary
            </h2>


            <div className="accuracy">


                <div>

                    <span>
                        Total Wards Analysed
                    </span>


                    <strong>
                        {summary.total_wards || 0}
                    </strong>

                </div>




                <div>

                    <span>
                        Highest Impact Score
                    </span>


                    <strong>
                    {Number(summary.highest_score || 0).toFixed(2)}
                    </strong>


                </div>




                <div>

                    <span>
                        Average Score
                    </span>


                    <strong>
                    {Number(summary.average_score || 0).toFixed(2)}
                    </strong>


                </div>



            </div>


        </div>









        <div className="charts-grid">


            <div className="chart-card">


                <h2>
                    Priority Distribution
                </h2>



                <ResponsiveContainer
                width="100%"
                height={320}
                >


                <PieChart>


                <Pie

                data={priorityData}

                dataKey="value"

                nameKey="name"

                outerRadius={110}

                >


                {

                priorityData.map(
                (item,index)=>(


                    <Cell

                    key={index}

                    fill={COLORS[index]}

                    />


                ))

                }


                </Pie>


                <Tooltip/>

                <Legend/>


                </PieChart>


                </ResponsiveContainer>


            </div>









            <div className="chart-card">


                <h2>
                    Top Priority Wards
                </h2>



                <ResponsiveContainer
                width="100%"
                height={320}
                >


                <BarChart
                data={topWards}
                >


                <XAxis
                dataKey="name"
                />


                <YAxis/>


                <Tooltip/>


                <Bar

                dataKey="score"

                fill="#22c55e"

                />


                </BarChart>


                </ResponsiveContainer>


            </div>


        </div>









        <div className="accuracy-card">


            <h2>

            <Trophy size={25}/>

            Top Priority Ward

            </h2>



            <h1>

            🌳 {summary.top_ward || "N/A"}

            </h1>



            <p>

            Impact Score:

            <b>

            {Number(summary.highest_score || 0).toFixed(2)}

            </b>

            </p>


        </div>









        <div className="outputs-card">


            <h2>
                Generated Outputs
            </h2>



            {

            outputs.map((item,index)=>(


                <div

                className="output-item"

                key={index}

                >


                    <CheckCircle size={20}/>


                    <span>
                        {item}
                    </span>


                </div>


            ))

            }






            <button

            className="report-download"

            onClick={downloadReport}

            >


                <Download size={18}/>


                Download Full Report


            </button>




        </div>






    </div>


    );


}