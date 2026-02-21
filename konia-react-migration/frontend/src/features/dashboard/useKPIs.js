import { useState, useEffect } from 'react';
import api from '../../api/axiosConfig';

export const useKPIs = (periodo) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchKPIs = async () => {
            if (!periodo) return;

            try {
                setLoading(true);
                setError(null);
                const response = await api.get(`/api/kpis/resumen?periodo=${periodo}`);
                setData(response.data);
            } catch (err) {
                console.error("Error fetching KPIs:", err);
                setError("No se pudieron cargar los indicadores clave.");
            } finally {
                setLoading(false);
            }
        };

        fetchKPIs();
    }, [periodo]);

    return { data, loading, error };
};
