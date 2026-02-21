import { create } from 'zustand';

const useFilterStore = create((set) => ({
    filters: {
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
        tipo: [], // ['I', 'E', 'N', 'P']
        metodo: [], // ['PUE', 'PPD']
        agrupacion: 'Mensual'
    },

    setFilter: (key, value) => set((state) => ({
        filters: { ...state.filters, [key]: value }
    })),

    resetFilters: () => set({
        filters: {
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1,
            tipo: [],
            metodo: [],
            agrupacion: 'Mensual'
        }
    })
}));

export default useFilterStore;
