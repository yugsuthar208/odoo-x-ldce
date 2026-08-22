import apiClient from "./apiClient";

export const authService = {
  login: (email, password) =>
    apiClient.post("/auth/login", { email, password }).then((r) => r.data),

  signup: (payload) =>
    apiClient.post("/auth/signup", payload).then((r) => r.data),

  forgotPassword: (email) =>
    apiClient.post("/auth/forgot-password", { email }).then((r) => r.data),

  getProfile: () =>
    apiClient.get("/users/me").then((r) => r.data),

  updateProfile: (payload) =>
    apiClient.put("/users/me", payload).then((r) => r.data),

  deleteAccount: () =>
    apiClient.delete("/users/me").then((r) => r.data),
};
