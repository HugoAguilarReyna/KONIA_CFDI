import React, { createContext, useState, useEffect, useContext } from 'react';
import authService from './authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkUser = async () => {
            try {
                const userData = await authService.getCurrentUser();
                setUser(userData);
            } catch (error) {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        checkUser();
    }, []);

    const login = async (username, password, company_id) => {
        try {
            const data = await authService.login(username, password, company_id);
            setUser(data.user);
            return { success: true };
        } catch (error) {
            console.error('Login error detail:', error);
            let message = 'Login failed';

            if (!error.response) {
                message = 'Network Error: Backend unreachable. Check API URL or CORS.';
            } else if (error.response.status === 401) {
                message = error.response.data?.detail || 'Invalid credentials';
            } else {
                message = `Server Error (${error.response.status}): ${error.response.data?.detail || 'Unknown error'}`;
            }

            return { success: false, message };
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
            setUser(null);
        } catch (error) {
            console.error('Logout error', error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
