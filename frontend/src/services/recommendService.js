import apiClient from "./apiClient";

export const recommendService = {
  getRecommendedCities: () =>
    apiClient.get("/recommend/cities").then((r) => r.data),

  getPredictedBudget: (tripId) =>
    apiClient.get(`/recommend/budget/${tripId}`).then((r) => r.data),
};
