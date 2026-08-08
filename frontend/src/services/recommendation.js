import api from "./api";

export const getRecommendations = async () => {
    const { data } = await api.get("/recommendations");
    return data;
};