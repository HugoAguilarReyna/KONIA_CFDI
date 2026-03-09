import { create } from 'zustand';

const useFilterStore = create((set) => ({
    filters: {
        empresa: 'TENANT_001',
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
        tipo: [], // ['I', 'E', 'N', 'P']
        metodo: [], // ['PUE', 'PPD']
        monto_min: null,
        monto_max: null,
        agrupacion: 'Mensual'
    },

    setFilter: (key, value) => set((state) => ({
        filters: { ...state.filters, [key]: value }
    })),

    resetFilters: () => set({
        filters: {
            empresa: 'TENANT_001',
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1,
            tipo: [],
            metodo: [],
            monto_min: null,
            monto_max: null,
            agrupacion: 'Mensual'
        }
    })
}));

export default useFilterStore;
