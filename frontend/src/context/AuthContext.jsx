/* eslint-disable react-refresh/only-export-components */
/* eslint-disable react-hooks/exhaustive-deps */
import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // We no longer check for tokens in JS. 
        // We trust the 'user' object for UI state. 
        // Real validation happens via Http-only cookies on first API call.
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = async (username, password, role) => {
        try {
            const response = await api.post('/auth/login', { username, password });
            const { user: serverUser } = response.data.data;

            // Tokens are set in Http-only cookies by the backend
            localStorage.setItem('user', JSON.stringify(serverUser));
            setUser(serverUser);
            return { success: true };
        } catch (err) {
            return { success: false, message: err.response?.data?.message || 'Login failed' };
        }
    };

    const register = async (userData) => {
        try {
            const response = await api.post('/auth/register', userData);
            return { success: true, data: response.data };
        } catch (err) {
            return { success: false, message: err.response?.data?.message || 'Registration failed' };
        }
    };

    const logout = async () => {
        try {
            await api.post('/auth/logout');
        } catch (err) {
            console.error("Logout API failed", err);
        } finally {
            localStorage.removeItem('user');
            localStorage.removeItem('access_token'); // Clean up legacy
            localStorage.removeItem('refresh_token'); // Clean up legacy
            setUser(null);
        }
    };

    // Idle Timeout (15m for users, 30m for admins)
    useEffect(() => {
        if (!user) return;

        let idleTimer;
        const idleLimit = user.role === 'admin' ? 30 * 60 * 1000 : 15 * 60 * 1000;

        const resetTimer = () => {
            clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                console.log("Idle timeout reached. Logging out...");
                logout();
            }, idleLimit);
        };

        // Events to track activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(event => document.addEventListener(event, resetTimer));

        resetTimer(); // Start timer

        return () => {
            clearTimeout(idleTimer);
            events.forEach(event => document.removeEventListener(event, resetTimer));
        };
    }, [user]);

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);

