import axios from 'axios';

// Create an Axios instance
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    withCredentials: true, // Important for HttpOnly cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor for handling 401s (token expiry)
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If error is 401, we haven't retried yet, AND the request was not a refresh attempt
        if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/refresh')) {
            originalRequest._retry = true;

            try {
                // Try to refresh token
                await api.post('/api/auth/refresh');
                // Retry original request
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, logout user (handled by AuthContext or similar)
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
