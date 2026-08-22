import apiClient from "./apiClient";

export const cityService = {
  getCities: (search = "", region = "") => {
    const params = {};
    if (search) params.search = search;
    if (region && region !== "All") params.region = region;
    return apiClient.get("/cities", { params }).then((r) => r.data);
  },

  getCityDetail: (id) =>
    apiClient.get(`/cities/${id}`).then((r) => r.data),

  getCityActivities: (id, type = "", maxCost = null) => {
    const params = {};
    if (type) params.type = type;
    if (maxCost) params.max_cost = maxCost;
    return apiClient.get(`/cities/${id}/activities`, { params }).then((r) => r.data);
  },
};
