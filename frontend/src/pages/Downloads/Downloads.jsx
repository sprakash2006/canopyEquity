import "./Downloads.css";

import {
    Download,
    FileText,
    Database,
    Map,
    Image,
    FileSpreadsheet,
    Loader2,
    CheckCircle,
    ArrowDownToLine,
    Files,
    Sparkles
} from "lucide-react";

import {
    useState
} from "react";


const API_URL = "http://localhost:8000";


const files = [

    {
        name: "AI Canopy Prediction",
        file: "canopy_prediction_web.tif",
        type: "GeoTIFF",
        icon: <Image />
    },

    {
        name: "Ward Rankings GeoJSON",
        file: "ward_rankings_web.geojson",
        type: "GIS Data",
        icon: <Map />
    },

    {
        name: "Dashboard Data",
        file: "dashboard_data.json",
        type: "JSON",
        icon: <Database />
    },

    {
        name: "Top Recommendations",
        file: "top10_recommendations.json",
        type: "AI Output",
        icon: <FileText />
    },

    {
        name: "Final Recommendations",
        file: "final_recommendations.csv",
        type: "CSV",
        icon: <FileSpreadsheet />
    },

    {
        name: "Optimized Plantation Plan",
        file: "optimized_plan.csv",
        type: "CSV",
        icon: <FileSpreadsheet />
    },

    {
        name: "AI Evaluation Report",
        file: "CanopyAI_Evaluation_Report.pdf",
        type: "PDF Report",
        icon: <FileText />
    }

];


export default function Downloads() {

    const [downloading, setDownloading] = useState("");


    const downloadFile = async (file) => {

        try {

            setDownloading(file);


            const url =
                `${API_URL}/outputs/${file}`;


            const response =
                await fetch(url);


            if (!response.ok) {

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

        catch (error) {

            console.error(
                "Download Error",
                error
            );


            alert(
                "File not available yet"
            );

        }

        finally {

            setDownloading("");

        }

    };


    return (

        <div className="downloads">


            {/* =================================================
                PAGE HEADER
            ================================================= */}

            <div className="downloads-header">

                <div className="downloads-title-row">

                    <div className="downloads-title-icon">

                        <ArrowDownToLine
                            size={19}
                            strokeWidth={2}
                        />

                    </div>


                    <div>

                        <div className="downloads-eyebrow">

                            <Sparkles
                                size={11}
                            />

                            AI OUTPUT CENTER

                        </div>


                        <h1>
                            Download AI Results
                        </h1>


                        <p>
                            Export generated GIS, AI and recommendation outputs
                        </p>

                    </div>

                </div>


                {/* =================================================
                    HEADER SUMMARY
                ================================================= */}

                <div className="downloads-summary">

                    <div className="summary-icon">

                        <Files
                            size={17}
                        />

                    </div>


                    <div>

                        <strong>
                            {files.length}
                        </strong>

                        <span>
                            Files Ready
                        </span>

                    </div>

                </div>

            </div>


            {/* =================================================
                OUTPUT CATEGORIES
            ================================================= */}

            <div className="downloads-section-header">

                <div>

                    <span>
                        GENERATED OUTPUTS
                    </span>

                    <h2>
                        Available Files
                    </h2>

                </div>


                <div className="ready-indicator">

                    <span />

                    All outputs ready

                </div>

            </div>


            {/* =================================================
                DOWNLOAD GRID
            ================================================= */}

            <div className="download-grid">

                {files.map((item, index) => (

                    <div
                        className="download-card"
                        key={index}
                    >


                        {/* CARD TOP */}

                        <div className="download-card-top">

                            <div className="file-icon">

                                {item.icon}

                            </div>


                            <span className="file-ready">

                                <CheckCircle
                                    size={11}
                                />

                                Ready

                            </span>

                        </div>


                        {/* FILE INFO */}

                        <div className="file-info">

                            <h3>
                                {item.name}
                            </h3>


                            <p>
                                {item.file}
                            </p>

                        </div>


                        {/* TYPE */}

                        <div className="file-meta">

                            <span className="file-type">

                                {item.type}

                            </span>


                            <span className="file-generated">

                                AI Generated

                            </span>

                        </div>


                        {/* DOWNLOAD */}

                        <button

                            className="download-button"

                            onClick={() =>
                                downloadFile(
                                    item.file
                                )
                            }

                            disabled={
                                downloading ===
                                item.file
                            }

                        >

                            {downloading === item.file ? (

                                <>

                                    <Loader2
                                        size={15}
                                        className="spin"
                                    />

                                    Downloading...

                                </>

                            ) : (

                                <>

                                    <Download
                                        size={15}
                                    />

                                    Download File

                                </>

                            )}

                        </button>

                    </div>

                ))}

            </div>


            {/* =================================================
                STATUS
            ================================================= */}

            <div className="download-status">

                <div className="status-icon">

                    <CheckCircle
                        size={16}
                    />

                </div>


                <div>

                    <strong>
                        All AI-generated outputs are ready
                    </strong>

                    <span>
                        GIS layers, model predictions and recommendation reports
                        are available for export.
                    </span>

                </div>

            </div>


        </div>

    );

}