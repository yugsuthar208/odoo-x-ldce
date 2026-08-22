import apiClient from "./apiClient";

export const favoriteService = {
  getFavorites: () =>
    apiClient.get("/favorites").then((r) => r.data),

  addFavorite: (payload) =>
    apiClient.post("/favorites", payload).then((r) => r.data),

  removeFavorite: (id) =>
    apiClient.delete(`/favorites/${id}`).then((r) => r.data),
};
