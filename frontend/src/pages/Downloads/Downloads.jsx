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
    Sparkles,
    BrainCircuit,
    BarChart3,
    Leaf,
    ShieldCheck
} from "lucide-react";

import {
    useEffect,
    useState
} from "react";

import {
    getReportStatus,
    generateFinalReport,
    downloadFinalReport
} from "../../services/api";


const API_URL =
    "http://localhost:8000";


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

    // ======================================================
    // EXISTING DOWNLOAD STATE
    // ======================================================

    const [
        downloading,
        setDownloading
    ] = useState("");


    // ======================================================
    // FINAL REPORT STATE
    // ======================================================

    const [
        generatingReport,
        setGeneratingReport
    ] = useState(false);


    const [
        reportReady,
        setReportReady
    ] = useState(false);


    const [
        reportError,
        setReportError
    ] = useState("");


    // ======================================================
    // CHECK REPORT STATUS
    // ======================================================

    const checkReportStatus = async () => {

        try {

            const response =
                await getReportStatus();

            setReportReady(
                response.data?.ready === true
            );

        }

        catch (error) {

            console.error(
                "Report Status Error:",
                error
            );

        }

    };


    // ======================================================
    // CHECK WHEN PAGE LOADS
    // ======================================================

    useEffect(() => {

        checkReportStatus();

    }, []);


    // ======================================================
    // GENERATE FINAL REPORT
    // ======================================================

    const handleGenerateReport =
        async () => {

            try {

                setGeneratingReport(true);

                setReportError("");

                const response =
                    await generateFinalReport();


                if (
                    response.data?.success
                ) {

                    setReportReady(true);

                }

                else {

                    throw new Error(
                        response.data?.message ||
                        "Report generation failed."
                    );

                }

            }

            catch (error) {

                console.error(
                    "Report Generation Error:",
                    error
                );


                const message =
                    error.response?.data?.detail?.message ||
                    error.response?.data?.detail ||
                    error.message ||
                    "Unable to generate report.";


                setReportError(
                    message
                );

            }

            finally {

                setGeneratingReport(
                    false
                );

            }

        };


    // ======================================================
    // DOWNLOAD FINAL REPORT
    // ======================================================

    const handleDownloadReport =
        async () => {

            try {

                setReportError("");

                await downloadFinalReport();

            }

            catch (error) {

                console.error(
                    "Report Download Error:",
                    error
                );

                setReportError(
                    "Unable to download the final report."
                );

            }

        };


    // ======================================================
    // EXISTING FILE DOWNLOAD
    // ======================================================

    const downloadFile =
        async (file) => {

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
                    document.createElement(
                        "a"
                    );


                const objectUrl =
                    window.URL.createObjectURL(
                        blob
                    );


                link.href =
                    objectUrl;


                link.download =
                    file;


                document.body.appendChild(
                    link
                );


                link.click();


                link.remove();


                window.URL.revokeObjectURL(
                    objectUrl
                );

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
                            Export generated GIS, AI and
                            recommendation outputs
                        </p>

                    </div>

                </div>


                {/* HEADER SUMMARY */}

                <div className="downloads-summary">

                    <div className="summary-icon">

                        <Files
                            size={17}
                        />

                    </div>


                    <div>

                        <strong>
                            {files.length + 1}
                        </strong>

                        <span>
                            Files Ready
                        </span>

                    </div>

                </div>

            </div>


            {/* =================================================
                FINAL EXPLAINABLE AI REPORT
            ================================================= */}

            <section className="final-report-card">

                <div className="final-report-main">


                    {/* ICON */}

                    <div className="final-report-icon">

                        <BrainCircuit
                            size={28}
                            strokeWidth={1.8}
                        />

                    </div>


                    {/* CONTENT */}

                    <div className="final-report-content">

                        <div className="final-report-eyebrow">

                            <Sparkles
                                size={12}
                            />

                            CANOPYAI DECISION REPORT

                        </div>


                        <h2>
                            Final Explainable AI Report
                        </h2>


                        <p>

                            Generate a comprehensive PDF
                            explaining the complete CanopyAI
                            analysis — from satellite imagery
                            and AI canopy prediction to model
                            evaluation, spatial impact scoring,
                            ward prioritization and plantation
                            recommendations.

                        </p>


                        {/* REPORT FEATURES */}

                        <div className="final-report-features">

                            <span>

                                <Map
                                    size={14}
                                />

                                Spatial Maps

                            </span>


                            <span>

                                <BrainCircuit
                                    size={14}
                                />

                                AI Analysis

                            </span>


                            <span>

                                <BarChart3
                                    size={14}
                                />

                                Model Metrics

                            </span>


                            <span>

                                <Leaf
                                    size={14}
                                />

                                Planting Strategy

                            </span>


                            <span>

                                <ShieldCheck
                                    size={14}
                                />

                                Explainable Results

                            </span>

                        </div>

                    </div>


                    {/* ACTION */}

                    <div className="final-report-action">

                        {!reportReady ? (

                            <button
                                className="generate-report-btn"
                                onClick={
                                    handleGenerateReport
                                }
                                disabled={
                                    generatingReport
                                }
                            >

                                {generatingReport ? (

                                    <>

                                        <Loader2
                                            size={17}
                                            className="spin"
                                        />

                                        Generating...

                                    </>

                                ) : (

                                    <>

                                        <FileText
                                            size={17}
                                        />

                                        Generate Report

                                    </>

                                )}

                            </button>

                        ) : (

                            <button
                                className="generate-report-btn report-download-btn"
                                onClick={
                                    handleDownloadReport
                                }
                            >

                                <Download
                                    size={17}
                                />

                                Download PDF

                            </button>

                        )}

                    </div>

                </div>


                {/* SUCCESS */}

                {reportReady && (

                    <div className="final-report-success">

                        <CheckCircle
                            size={16}
                        />

                        <span>

                            Final explainable AI report
                            is ready for download.

                        </span>

                        <span className="report-status-badge">

                            PDF READY

                        </span>

                    </div>

                )}


                {/* ERROR */}

                {reportError && (

                    <div className="final-report-error">

                        <span>
                            {reportError}
                        </span>

                    </div>

                )}

            </section>


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

                {files.map(
                    (item, index) => (

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

                                {downloading ===
                                item.file ? (

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

                    )
                )}

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
                        GIS layers, model predictions and
                        recommendation reports are available
                        for export.
                    </span>

                </div>

            </div>


        </div>

    );

}