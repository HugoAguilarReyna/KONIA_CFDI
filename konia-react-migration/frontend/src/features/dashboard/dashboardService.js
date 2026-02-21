import api from '../../api/axiosConfig';

const dashboardService = {
    getMatrizResumen: async (filters) => {
        // Convert filters to query params
        const params = new URLSearchParams();

        // Handle period construction
        if (filters.periodo) {
            params.append('periodo', filters.periodo);
        } else if (filters.year && filters.month) {
            const m = filters.month.toString().padStart(2, '0');
            params.append('periodo', `${filters.year}-${m}`);
        }

        const response = await api.get(`/api/dashboard/matriz-resumen?${params.toString()}`);
        return response.data;
    },

    getMatrizEvolucion: async () => {
        try {
            const response = await api.get('/api/dashboard/matriz-resumen/evolucion');
            return response.data;
        } catch (error) {
            console.error("Service Error getMatrizEvolucion:", error);
            return { evolucion: [] };
        }
    },

    getMatrizTabla: async (periodo) => {
        try {
            const response = await api.get(`/api/dashboard/matriz-resumen/tabla?periodo=${periodo}`);
            return response.data;
        } catch (error) {
            console.error("Service Error getMatrizTabla:", error);
            // Return empty structure to prevent crashes
            return {
                periodo_actual: periodo,
                periodo_anterior: null,
                matriz_actual: { PPD: {}, PUE: {} },
                matriz_anterior: { PPD: {}, PUE: {} }
            };
        }
    },

    getDetalleUUID: async (periodo, page = 1, limit = 25, filters = {}) => {
        const params = new URLSearchParams();
        params.append('periodo', periodo);
        params.append('page', page);
        params.append('limit', limit);

        if (filters.flujo) params.append('flujo', filters.flujo);
        if (filters.segmento) params.append('segmento', filters.segmento);
        if (filters.uuid_search) params.append('uuid_search', filters.uuid_search);
        if (filters.saldo_min !== undefined && filters.saldo_min !== null) params.append('saldo_min', filters.saldo_min);

        const response = await api.get(`/api/dashboard/detalle-uuid?${params.toString()}`);
        return response.data;
    },

    getUuidsDisponibles: async (periodo, page = 1, limit = 50) => {
        const params = new URLSearchParams();
        if (periodo) params.append('periodo', periodo);
        params.append('page', page);
        params.append('limit', limit);
        const response = await api.get(`/api/dashboard/trazabilidad/uuids?${params.toString()}`);
        return response.data;
    },

    getTrazabilidad: async (uuid_raiz) => {
        const response = await api.get(`/api/dashboard/trazabilidad/${uuid_raiz}`);
        return response.data;
    },

    getDimTiempo: async (periodo) => {
        const response = await api.get(`/api/dashboard/dim-tiempo/${periodo}`);
        return response.data;
    },

    getRiskAnalysis: async (uuid) => {
        const response = await api.get(`/api/dashboard/riesgos/${uuid}`);
        return response.data;
    }
};

export default dashboardService;
