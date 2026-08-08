import api from "./api";

export const getWardData = async () => {
    const { data } = await api.get("/wards");
    return data;
};

export const getPrediction = async () => {
    return `${api.defaults.baseURL}/prediction`;
};