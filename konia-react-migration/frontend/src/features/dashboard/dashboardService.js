import api from '../../api/axiosConfig';
import useFilterStore from '../../stores/useFilterStore'; const dashboardService = {
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
        if (filters.tipo && filters.tipo.length > 0) {
            params.append('tipo', filters.tipo.join(','));
        }
        if (filters.metodo && filters.metodo.length > 0) {
            params.append('metodo', filters.metodo.join(','));
        }

        // Add amount range filters
        if (filters.monto_min !== undefined && filters.monto_min !== null) params.append('monto_min', filters.monto_min);
        if (filters.monto_max !== undefined && filters.monto_max !== null) params.append('monto_max', filters.monto_max);

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
            const params = new URLSearchParams({ periodo });

            // Retrieve global filters directly if available or pass as argument
            const globalFilters = useFilterStore.getState().filters;
            if (globalFilters.tipo && globalFilters.tipo.length > 0) params.append('tipo', globalFilters.tipo.join(','));
            if (globalFilters.metodo && globalFilters.metodo.length > 0) params.append('metodo', globalFilters.metodo.join(','));
            if (globalFilters.monto_min !== undefined && globalFilters.monto_min !== null) params.append('monto_min', globalFilters.monto_min);
            if (globalFilters.monto_max !== undefined && globalFilters.monto_max !== null) params.append('monto_max', globalFilters.monto_max);

            const response = await api.get(`/api/dashboard/matriz-resumen/tabla?${params.toString()}`);
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

        // Use global store if filters object doesn't provide them
        const globalFilters = useFilterStore.getState().filters;
        const tipo = filters.tipo || globalFilters.tipo;
        const metodo = filters.metodo || globalFilters.metodo;
        const monto_min = filters.monto_min !== undefined ? filters.monto_min : globalFilters.monto_min;
        const monto_max = filters.monto_max !== undefined ? filters.monto_max : globalFilters.monto_max;

        if (tipo && tipo.length > 0) params.append('tipo', tipo.join(','));
        if (metodo && metodo.length > 0) params.append('metodo', metodo.join(','));
        if (monto_min !== undefined && monto_min !== null) params.append('monto_min', monto_min);
        if (monto_max !== undefined && monto_max !== null) params.append('monto_max', monto_max);

        const response = await api.get(`/api/dashboard/detalle-uuid?${params.toString()}`);
        return response.data;
    },

    getUuidsDisponibles: async (periodo, page = 1, limit = 50, filters = {}) => {
        const params = new URLSearchParams();
        if (periodo) params.append('periodo', periodo);
        params.append('page', page);
        params.append('limit', limit);
        if (filters.uuid_search) params.append('uuid_search', filters.uuid_search);
        if (filters.eventos_filter) params.append('eventos_filter', filters.eventos_filter);
        if (filters.estado_filter) params.append('estado_filter', filters.estado_filter);
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
