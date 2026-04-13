import axios from 'axios';

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Crucial for cookie-based auth
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor: attach Authorization header from localStorage (fallback for cross-site issues)
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token && !config.headers['Authorization']) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for handling 401 and token refresh
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        // Skip interceptor logic for auth endpoints specifically
        if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/refresh')) {
            return Promise.reject(error);
        }

        // If 401 error and not already retried
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Try to get a new access token via refresh cookie
                await axios.post(
                    `${API_BASE_URL}/auth/refresh`,
                    {},
                    { withCredentials: true }
                );

                // Retry the original request (now with refreshed cookie and Authorization header)
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh token failed or expired, force logout
                localStorage.removeItem('user');
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login?session_expired=true';
            }
        }

        // Handle generic Network Errors
        if (!error.response) {
            return Promise.reject(new Error("Network Error: Server unreachable."));
        }

        return Promise.reject(error);
    }
);

export default api;

