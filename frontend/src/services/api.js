import axios from "axios";

const api = axios.create({

    baseURL: "http://127.0.0.1:8000",

    timeout: 600000

});


// ==========================================================
// HEALTH
// ==========================================================

export const getHealth = () =>

    api.get("/health");


// ==========================================================
// STATUS
// ==========================================================

export const getStatus = () =>

    api.get("/status");


// ==========================================================
// PIPELINE STATUS
// ==========================================================

export const getPipelineStatus = () =>

    api.get("/pipeline-status");


// ==========================================================
// DASHBOARD
// ==========================================================

export const getDashboard = () =>

    api.get("/dashboard");


// ==========================================================
// STATISTICS
// ==========================================================

export const getStatistics = () =>

    api.get("/statistics");


// ==========================================================
// RECOMMENDATIONS
// ==========================================================

export const getRecommendations = () =>

    api.get("/recommendations");


// ==========================================================
// WARD RANKINGS
// ==========================================================

export const getWardRankings = () =>

    api.get("/ward-rankings");


// ==========================================================
// UPLOAD IMAGE
// ==========================================================

export const uploadImage = (

    file,

    onUploadProgress

) => {

    const formData = new FormData();


    formData.append(

        "file",

        file

    );


    return api.post(

        "/upload",

        formData,

        {

            headers: {

                "Content-Type":

                    "multipart/form-data"

            },

            onUploadProgress

        }

    );

};


// ==========================================================
// RUN COMPLETE AI PIPELINE
// ==========================================================

export const runPrediction = () =>

    api.post("/predict");


// ==========================================================
// DOWNLOAD OUTPUT FILE
// ==========================================================

export const downloadOutput = (filename) => {

    return (

        `${api.defaults.baseURL}/outputs/${filename}`

    );

};


// ==========================================================
// FINAL AI EXPLAINABLE REPORT
// ==========================================================

export const getReportStatus = () => {

    return api.get(

        "/report/status"

    );

};


// ==========================================================
// GENERATE FINAL REPORT
// ==========================================================

export const generateFinalReport = () => {

    return api.post(

        "/report/generate"

    );

};


// ==========================================================
// DOWNLOAD FINAL REPORT
// ==========================================================

export const downloadFinalReport = async () => {

    const response = await api.get(

        "/report/download",

        {

            responseType: "blob"

        }

    );


    const blob = response.data;


    const url = window.URL.createObjectURL(

        blob

    );


    const link = document.createElement(

        "a"

    );


    link.href = url;


    link.download =

        "CanopyAI_Final_Report.pdf";


    document.body.appendChild(

        link

    );


    link.click();


    link.remove();


    window.URL.revokeObjectURL(

        url

    );


    return response;

};


// ==========================================================
// DEFAULT AXIOS INSTANCE
// ==========================================================

export default api;