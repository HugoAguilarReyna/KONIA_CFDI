import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronDown } from 'lucide-react';
import useUIStore from '../../stores/useUIStore';
import useFilterStore from '../../stores/useFilterStore';

const Sidebar = ({ variant = 'mobile' }) => {
    const { isSidebarOpen, closeSidebar } = useUIStore();
    const { filters, setFilter } = useFilterStore();
    // Desktop collapse state
    const [isCollapsed, setIsCollapsed] = useState(false);

    // --- Content Component ---
    const SidebarContent = () => (
        <div
            className="flex flex-col h-full text-white relative overflow-hidden"
            style={{ background: 'linear-gradient(160deg, #5b6ec4 0%, #6a5eae 50%, #7952a0 100%)' }}
        >
            {/* Texture Overlay */}
            <div
                className="absolute inset-0 pointer-events-none opacity-[0.03] z-0"
                style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/stardust.png")' }}
            />

            {/* Header: FILTROS */}
            <div className="p-6 pb-4 relative z-10">
                <span className="font-bold text-lg text-white tracking-widest uppercase">FILTROS</span>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar px-6 space-y-8 pb-8 pt-2 relative z-10">
                {/* --- TIPO COMPROBANTE --- */}
                <div className="space-y-4 pt-2">
                    <label className="text-[11px] font-bold text-white/70 uppercase tracking-widest mb-2 block">TIPO COMPROBANTE</label>
                    <div className="flex flex-wrap gap-3">
                        {['Egreso', 'Ingreso', 'Nómina', 'Pago'].map(type => {
                            const isSelected = filters.tipo?.includes(type);
                            return (
                                <motion.button
                                    key={type}
                                    whileHover={{ scale: 1.05, x: 2 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => {
                                        const current = filters.tipo || [];
                                        const next = current.includes(type)
                                            ? current.filter(t => t !== type)
                                            : [...current, type];
                                        setFilter('tipo', next);
                                    }}
                                    className={`text-xs transition-all duration-200 px-4 py-2 rounded-full border ${isSelected
                                        ? 'bg-white/95 text-[#5b6ec4] font-bold border-transparent shadow-[0_4px_12px_rgba(0,0,0,0.2)]'
                                        : 'bg-white/10 text-white border-white/25 hover:bg-white/20'
                                        }`}
                                >
                                    {type}
                                </motion.button>
                            );
                        })}
                    </div>
                </div>

                {/* --- MÉTODO DE PAGO --- */}
                <div className="space-y-4 pt-2">
                    <label className="text-[11px] font-bold text-white/70 uppercase tracking-widest mb-2 block">MÉTODO DE PAGO</label>
                    <div className="flex flex-wrap gap-3">
                        {['Otros', 'PPD (Pago Diferido)', 'PUE (Pago Una Exhib.)'].map(method => {
                            const isSelected = filters.metodo?.includes(method);
                            return (
                                <motion.button
                                    key={method}
                                    whileHover={{ scale: 1.05, x: 2 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => {
                                        const current = filters.metodo || [];
                                        const next = current.includes(method) ? current.filter(m => m !== method) : [...current, method];
                                        setFilter('metodo', next);
                                    }}
                                    className={`text-xs transition-all duration-200 px-4 py-2 rounded-full border ${isSelected
                                        ? 'bg-white/95 text-[#5b6ec4] font-bold border-transparent shadow-[0_4px_12px_rgba(0,0,0,0.2)]'
                                        : 'bg-white/10 text-white border-white/25 hover:bg-white/20'
                                        }`}
                                >
                                    {method}
                                </motion.button>
                            );
                        })}
                    </div>
                </div>

                {/* --- PERIODO FISCAL --- */}
                <div className="space-y-4 pt-2">
                    <label className="text-[11px] font-bold text-white/70 uppercase tracking-widest mb-2 block">PERIODO FISCAL</label>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1">
                            <label className="text-[10px] text-white/50 uppercase tracking-tighter">Año</label>
                            <div className="relative">
                                <select
                                    value={filters.year || 2026}
                                    onChange={(e) => setFilter('year', parseInt(e.target.value))}
                                    className="w-full appearance-none bg-black/20 border border-white/20 rounded-[10px] py-2 px-3 text-sm text-white focus:outline-none focus:border-white/60 focus:ring-4 focus:ring-white/5 transition-all"
                                >
                                    {[2026, 2025, 2024, 2023].map(y => <option key={y} value={y} className="bg-[#6a5eae]">{y}</option>)}
                                </select>
                                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 pointer-events-none" />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-[10px] text-white/50 uppercase tracking-tighter">Mes</label>
                            <div className="relative">
                                <select
                                    value={filters.month || 2}
                                    onChange={(e) => setFilter('month', parseInt(e.target.value))}
                                    className="w-full appearance-none bg-black/20 border border-white/20 rounded-[10px] py-2 px-3 text-sm text-white focus:outline-none focus:border-white/60 focus:ring-4 focus:ring-white/5 transition-all"
                                >
                                    {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                                        <option key={m} value={m} className="bg-[#6a5eae]">{new Date(0, m - 1).toLocaleString('es-MX', { month: 'long' }).charAt(0).toUpperCase() + new Date(0, m - 1).toLocaleString('es-MX', { month: 'long' }).slice(1)}</option>
                                    ))}
                                </select>
                                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 pointer-events-none" />
                            </div>
                        </div>
                    </div>

                    {/* Period Badge */}
                    <div className="bg-emerald-500/15 border border-emerald-500/40 rounded-[8px] p-3 flex items-center gap-3">
                        <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span className="text-[12px] font-medium text-emerald-400 flex items-center gap-1">
                            <span className="text-[14px]">✓</span>
                            Período: {new Date(0, (filters.month || 2) - 1).toLocaleString('es-MX', { month: 'long' }).charAt(0).toUpperCase() + new Date(0, (filters.month || 2) - 1).toLocaleString('es-MX', { month: 'long' }).slice(1)} {filters.year || 2026}
                        </span>
                    </div>
                </div>
            </div>

            {/* Version Footer */}
            <div className="p-6 bg-black/10 relative z-10">
                <p className="text-[11px] text-center text-white/40 tracking-widest font-medium uppercase transition-colors">
                    INTELIGENCIA FORENSE v2.0.1
                </p>
            </div>
        </div>
    );

    // --- Variant: Desktop ---
    if (variant === 'desktop') {
        const collapsedWidth = 0;
        const expandWidth = 270;

        return (
            <div
                className="relative h-full transition-all duration-300 ease-in-out flex-shrink-0 z-40"
                style={{ width: isCollapsed ? collapsedWidth : expandWidth }}
            >
                {/* Vertical Toggle Button - Final Refinement */}
                <motion.button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="absolute -right-[36px] top-[100px] w-[36px] h-[160px] text-white rounded-r-[18px] flex items-center justify-center cursor-pointer transition-all shadow-2xl z-50 overflow-hidden border-none"
                    style={{ background: 'linear-gradient(160deg, #5b6ec4 0%, #6a5eae 50%, #7952a0 100%)' }}
                    whileHover={{ x: 4 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                    <div className="flex flex-col items-center gap-4 h-full py-5">
                        {/* Hamburger Icon */}
                        <div className="flex flex-col gap-1.5 opacity-100 mb-1">
                            <div className="w-5 h-[3px] bg-white rounded-full"></div>
                            <div className="w-5 h-[3px] bg-white rounded-full"></div>
                            <div className="w-5 h-[3px] bg-white rounded-full"></div>
                        </div>
                        {/* Rotated Text - F at top */}
                        <span
                            className="font-bold text-[13px] tracking-[0.2em] whitespace-nowrap text-white"
                            style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
                        >
                            FILTROS
                        </span>
                    </div>
                </motion.button>

                {/* Content Container */}
                <div
                    className={`h-full w-[270px] overflow-hidden ${isCollapsed ? 'hidden' : 'block'}`}
                    style={{ background: 'linear-gradient(160deg, #5b6ec4 0%, #6a5eae 50%, #7952a0 100%)' }}
                >
                    <SidebarContent />
                </div>
            </div>
        );
    }

    // --- Variant: Mobile ---
    return (
        <AnimatePresence>
            {isSidebarOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        onClick={closeSidebar}
                        className="fixed inset-0 bg-black z-40 lg:hidden"
                    />
                    <motion.aside
                        initial={{ x: "-100%" }}
                        animate={{ x: 0 }}
                        exit={{ x: "-100%" }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="fixed top-0 left-0 h-full w-[280px] z-50 shadow-2xl"
                        style={{ background: 'linear-gradient(160deg, #5b6ec4 0%, #6a5eae 50%, #7952a0 100%)' }}
                    >
                        <div className="flex justify-end p-4">
                            <button onClick={closeSidebar}><X size={24} className="text-white/60 hover:text-white" /></button>
                        </div>
                        <SidebarContent />
                    </motion.aside>
                </>
            )}
        </AnimatePresence>
    );
};

export default Sidebar;
