import { create } from 'zustand';

const useUIStore = create((set) => ({
    isSidebarOpen: window.innerWidth >= 1024,
    activeModule: 'cuenta-t',
    activeSubTab: {
        'cuenta-t': '/',
        'materialidad': '/materialidad',
        'riesgos': '/riesgos',
        'compliance': '/compliance',
        'configuracion': '/configuracion'
    },

    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    closeSidebar: () => set({ isSidebarOpen: false }),
    openSidebar: () => set({ isSidebarOpen: true }),

    setActiveModule: (module) => set({ activeModule: module }),
    setActiveSubTab: (module, path) => set((state) => ({
        activeSubTab: {
            ...state.activeSubTab,
            [module]: path
        }
    })),
}));

export default useUIStore;
