import React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import useUIStore from '../../stores/useUIStore';
import { useAuth } from '../../features/auth/AuthContext';

const Navbar = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [openDropdown, setOpenDropdown] = React.useState(null);
    const dropdownRef = React.useRef(null);

    // Dropdown items definition
    const menuStructure = {
        'cuenta-t': {
            label: 'Cuenta T',
            items: [
                { label: 'KPIS', path: '/kpis' },
                { label: 'UUID', path: '/' },
                { label: 'Analítica', path: '/analitica' },
                { label: 'Prellenado', path: '/prellenado' },
            ]
        },
        'materialidad': {
            label: 'Materialidad / REPSE',
            items: [
                { label: 'Normativa', path: '/materialidad' },
                { label: 'Documentos', path: '/materialidad/documentos' },
                { label: 'Seguimiento', path: '/materialidad/seguimiento' },
            ]
        },
        'riesgos': {
            label: 'Riesgos',
            items: [
                { label: 'Detección de Anomalías', path: '/riesgos' },
                { label: 'Ranking de Riesgo', path: '/riesgos/ranking' },
            ]
        },
        'compliance': {
            label: 'Compliance',
            items: [
                { label: 'Auditoría de Tasas', path: '/compliance' },
                { label: 'Integridad de Flujo', path: '/compliance/integridad' },
                { label: 'Saldos IVA', path: '/compliance/saldos' },
                { label: 'Pagos Provisionales', path: '/compliance/pagos' },
            ]
        },
        'configuracion': {
            label: 'Configuración',
            items: [
                { label: 'General', path: '/configuracion' },
                { label: 'Modelos AI', path: '/configuracion/modelos' },
            ]
        },
    };

    const navItems = Object.entries(menuStructure).map(([id, info]) => ({
        id,
        label: info.label,
        path: info.items[0].path
    }));

    // Click outside handler
    React.useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpenDropdown(null);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const { activeModule, activeSubTab, setActiveModule, setActiveSubTab } = useUIStore();

    const handleItemClick = (moduleId, path) => {
        setActiveModule(moduleId);
        setActiveSubTab(moduleId, path);
        navigate(path);
        setOpenDropdown(null);
    };

    const isActive = (id) => {
        return activeModule === id;
    };

    // Add logout specifically for account menu
    const { logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav
            className="fixed top-0 w-full h-[50px] z-50 flex items-center justify-between px-6 shadow-md"
            style={{ background: 'linear-gradient(90deg, #5b6ec4 0%, #6a5eae 50%, #7952a0 100%)' }}
        >
            {/* Left: Logo */}
            <div className="flex items-center gap-3">
                <span className="font-bold text-[18px] text-white tracking-wide">KONIA</span>
            </div>

            {/* Right Group: Navigation + Utilities */}
            <div className="flex items-center gap-4" ref={dropdownRef}>
                {/* Navigation Pills */}
                <div className="flex items-center gap-2">
                    {navItems.map((item) => {
                        const active = isActive(item.id);
                        const isOpen = openDropdown === item.id;

                        return (
                            <div key={item.id} className="relative">
                                <button
                                    onClick={() => {
                                        if (activeModule !== item.id) {
                                            const lastPath = activeSubTab[item.id];
                                            handleItemClick(item.id, lastPath);
                                            setOpenDropdown(item.id);
                                        } else {
                                            setOpenDropdown(isOpen ? null : item.id);
                                        }
                                    }}
                                    style={{ fontFamily: "Montserrat" }}
                                    className={`
                                        px-4 py-1.5 rounded-[8px] text-[15px] font-medium transition-all duration-200
                                        ${active
                                            ? 'bg-white/25 text-white'
                                            : 'text-white hover:bg-white/10'
                                        }
                                    `}
                                >
                                    {item.label}
                                </button>

                                <AnimatePresence>
                                    {isOpen && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -8, scale: 0.97 }}
                                            animate={{ opacity: 1, y: 0, scale: 1 }}
                                            exit={{ opacity: 0, y: -8, scale: 0.97 }}
                                            transition={{ duration: 0.15 }}
                                            className="absolute left-0 mt-2 w-[260px] bg-[#6a5eae] shadow-md rounded-[12px] py-1.5 z-[60] overflow-hidden border border-white/10"
                                        >
                                            {menuStructure[item.id].items.map((subItem) => {
                                                const isSubActive = location.pathname === subItem.path ||
                                                    (subItem.path === '/' && location.pathname === '/dashboard');

                                                return (
                                                    <button
                                                        key={subItem.path}
                                                        onClick={() => handleItemClick(item.id, subItem.path)}
                                                        style={{ fontFamily: "Montserrat" }}
                                                        className={`
                                                            w-[calc(100%-16px)] text-left px-5 py-2.5 transition-all duration-200
                                                            text-[15px] mx-2 my-1 rounded-[8px]
                                                            ${isSubActive
                                                                ? 'bg-[#7c5cbf] text-white font-bold'
                                                                : 'text-white font-normal hover:bg-white/10'
                                                            }
                                                        `}
                                                    >
                                                        {subItem.label}
                                                    </button>
                                                );
                                            })}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        );
                    })}
                </div>

                {/* Vertical Divider */}
                <div className="w-[1px] h-6 bg-white/20 mx-1"></div>

                {/* Right Utilities (Grid + User Account) */}
                <div className="flex items-center gap-3">
                    {/* Grid Icon */}
                    <button className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M4 4h4v4H4V4zm6 0h4v4h-4V4zm6 0h4v4h-4V4zM4 10h4v4H4v-4zm6 0h4v4h-4v-4zm6 0h4v4h-4v-4zM4 16h4v4H4v-4zm6 0h4v4h-4v-4zm6 0h4v4h-4v-4z" />
                        </svg>
                    </button>

                    {/* User Profile */}
                    <div className="relative">
                        <button
                            onClick={() => setOpenDropdown(openDropdown === 'account' ? null : 'account')}
                            className="flex items-center gap-2 p-1 pl-2 pr-1 rounded-full hover:bg-white/10 transition-colors group"
                        >
                            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                                </svg>
                            </div>
                        </button>

                        <AnimatePresence>
                            {openDropdown === 'account' && (
                                <motion.div
                                    initial={{ opacity: 0, y: -8, scale: 0.97 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: -8, scale: 0.97 }}
                                    transition={{ duration: 0.15 }}
                                    className="absolute right-0 mt-2 w-[220px] bg-[#6a5eae] shadow-md rounded-[12px] py-2 z-[60] overflow-hidden border border-white/10"
                                >
                                    <div className="px-5 py-3 border-b border-white/10">
                                        <p className="text-white text-[14px] font-bold">Usuario Konia</p>
                                        <p className="text-white/60 text-[12px]">admin@konia.mx</p>
                                    </div>
                                    <button
                                        onClick={handleLogout}
                                        className="w-full text-left px-5 py-3 text-white text-[15px] hover:bg-white/10 transition-all duration-200 mt-1"
                                    >
                                        Salir
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
