import axios from "axios";

const BASE_URL = "http://localhost:8000/api";
const TOKEN_KEY = "tripora_token";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

/* ---- Request interceptor: attach JWT ---- */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

/* ---- Response interceptor: unwrap data, handle 401 ---- */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      // Let AuthContext and ProtectedRoute handle the redirect
    }
    const message =
      error.response?.data?.error ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

export { TOKEN_KEY };
export default apiClient;
