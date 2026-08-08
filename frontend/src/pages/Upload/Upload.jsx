import "./Upload.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    UploadCloud,
    Play,
    CheckCircle,
    Loader2
} from "lucide-react";

import {
    uploadImage,
    runPrediction
} from "../../services/api";

export default function Upload() {

    const navigate = useNavigate();

    const [file, setFile] = useState(null);

    const [uploading, setUploading] = useState(false);

    const [progress, setProgress] = useState(0);

    const [message, setMessage] = useState("");

    // ======================================================
    // FILE SELECT
    // ======================================================

    const handleFileChange = (event) => {

        if (event.target.files.length > 0) {

            setFile(event.target.files[0]);

            setMessage("");

            setProgress(0);

        }

    };

    // ======================================================
    // UPLOAD + RUN AI
    // ======================================================

    const handleAnalyze = async () => {

        if (!file) {

            alert("Please select a GeoTIFF (.tif/.tiff) file.");

            return;

        }

        try {

            setUploading(true);

            setProgress(0);

            setMessage("Uploading satellite image...");

            await uploadImage(

                file,

                (event) => {

                    if (!event.total) return;

                    const percent = Math.round(

                        (event.loaded * 100) / event.total

                    );

                    setProgress(percent);

                }

            );

            setProgress(100);

            setMessage("Upload completed.");

            await new Promise(resolve => setTimeout(resolve, 500));

            setProgress(0);

            setMessage("Running AI Engine...");

            await runPrediction();

            setProgress(100);

            setMessage("Analysis completed successfully.");

            localStorage.setItem(

                "dashboardRefresh",

                Date.now().toString()

            );

            setTimeout(() => {

                navigate("/", {

                    replace: true

                });

            }, 1200);

        }

        catch (error) {

            console.error(error);

            setMessage("Analysis failed.");

            setProgress(0);

        }

        finally {

            setUploading(false);

        }

    };

    return (

        <div className="upload-page">

            <div className="upload-card">

                <UploadCloud

                    size={70}

                    color="#22c55e"

                />

                <h2>

                    Upload Satellite Image

                </h2>

                <p>

                    Select Sentinel / GeoTIFF (.tif / .tiff)

                </p>

                <input

                    type="file"

                    accept=".tif,.tiff"

                    onChange={handleFileChange}

                />

                {

                    file && (

                        <p>

                            <strong>

                                {file.name}

                            </strong>

                        </p>

                    )

                }

                <button

                    className="upload-btn"

                    disabled={uploading}

                    onClick={handleAnalyze}

                >

                    {

                        uploading ?

                            <>

                                <Loader2

                                    size={18}

                                    className="spin"

                                />

                                Processing...

                            </>

                            :

                            <>

                                <Play size={18} />

                                Upload & Analyze

                            </>

                    }

                </button>

                {

                    uploading && (

                        <div style={{ marginTop: "20px" }}>

                            <progress

                                value={progress}

                                max="100"

                                style={{

                                    width: "100%",

                                    height: "10px"

                                }}

                            />

                            <p style={{

                                color: "white",

                                marginTop: "8px"

                            }}>

                                {progress}%

                            </p>

                        </div>

                    )

                }

                {

                    message && (

                        <div className="upload-status">

                            <CheckCircle size={18} />

                            {message}

                        </div>

                    )

                }

            </div>

        </div>

    );

}