import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000/api',
    withCredentials: true, // Crucial for cookie-based auth
    headers: {
        'Content-Type': 'application/json'
    }
});

// Response interceptor for handling 401 and token refresh
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        
        // If 401 error and not already retried
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // Try to get a new access token via refresh cookie
                // No need to pass tokens manually; browser sends the refresh cookie
                await axios.post('http://localhost:5000/api/auth/refresh', {}, {
                    withCredentials: true
                });
                
                // Retry the original request (now it has a valid access cookie)
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh token failed or expired, force logout
                localStorage.removeItem('user');
                localStorage.removeItem('access_token'); // Clean up legacy
                localStorage.removeItem('refresh_token'); // Clean up legacy
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

