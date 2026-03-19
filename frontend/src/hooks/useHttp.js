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
            setData(response.data.data || response.data);
            return response.data.data || response.data;
        } catch (err) {
            const message = err.response?.data?.message || err.message || 'Something went wrong';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const clearError = () => setError(null);

    return { loading, error, data, request, clearError };
};
