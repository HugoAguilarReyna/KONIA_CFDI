import api from '../../api/axiosConfig';

const authService = {
    login: async (username, password, company_id) => {
        const response = await api.post('/api/auth/login', { username, password, company_id });
        return response.data;
    },

    logout: async () => {
        await api.post('/api/auth/logout');
    },

    getCurrentUser: async () => {
        try {
            const response = await api.get('/api/auth/me');
            return response.data;
        } catch (error) {
            return null;
        }
    },
};

export default authService;
