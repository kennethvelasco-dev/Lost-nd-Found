import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor for JWT
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for handling 401 and token refresh
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        
        // If 401 error and not already retried
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (refreshToken) {
                try {
                    // Try to get a new access token
                    const response = await axios.post('http://localhost:5000/api/auth/refresh', {}, {
                        headers: { Authorization: `Bearer ${refreshToken}` }
                    });
                    
                    const { access_token } = response.data.data;
                    localStorage.setItem('access_token', access_token);
                    
                    // Update header and retry
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return axios(originalRequest);
                } catch (refreshError) {
                    // Refresh token failed, force logout
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login?session_expired=true';
                }
            } else {
                window.location.href = '/login';
            }
        }
        // Handle generic Network Errors (Server offline)
        if (!error.response) {
            console.error("Network Error: Backend is unreachable.");
            // If we have an access token, it might be a connectivity issue. 
            // We'll let the component handle the specific message, 
            // but we ensure the interceptor doesn't hang.
            return Promise.reject(new Error("Network Error: Server unreachable. Please check your connection or try again later."));
        }

        return Promise.reject(error);
    }
);

export default api;

