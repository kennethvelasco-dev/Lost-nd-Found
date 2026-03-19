import { useState, useCallback } from 'react';
import api from '../services/api';

export const useHttp = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    const request = useCallback(async (config) => {
        setLoading(true);
        setError(null);
        try {
            const response = await api(config);
            // Defensive data extraction: Ensure we always get the inner payload if wrapped
            const payload = response.data?.data !== undefined ? response.data.data : response.data;
            setData(payload);
            return payload;
        } catch (err) {
            const errorMsg = err.response?.data?.message || err.message || 'An unexpected error occurred';
            const errorCode = err.response?.data?.error_code || 'NETWORK_ERROR';
            
            console.error(`[API Error] ${config.method?.toUpperCase() || 'GET'} ${config.url}:`, {
                code: errorCode,
                message: errorMsg,
                details: err.response?.data
            });

            setError(errorMsg);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const clearError = () => setError(null);

    return { loading, error, data, request, clearError };
};
