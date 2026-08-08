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
// DEFAULT AXIOS INSTANCE
// ==========================================================

export default api;