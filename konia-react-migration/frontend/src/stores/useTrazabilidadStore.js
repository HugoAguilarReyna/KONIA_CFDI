import { create } from "zustand"

export const useTrazabilidadStore = create((set) => ({
    uuidSeleccionado: null,
    setUUIDTrazabilidad: (uuid) => set({ uuidSeleccionado: uuid })
}))
