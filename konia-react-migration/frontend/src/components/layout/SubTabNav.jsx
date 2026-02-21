import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import useUIStore from '../../stores/useUIStore';

const SubTabNav = () => {
    const { activeModule, activeSubTab, setActiveSubTab } = useUIStore();
    const navigate = useNavigate();
    const location = useLocation();

    // Mapping of modules to their sub-items
    const moduleConfig = {
        'uuid': [
            { label: 'Matriz Resumen', path: '/' },
            { label: 'Detalle UUID', path: '/detalle-uuid' },
            { label: 'Trazabilidad UUID', path: '/trazabilidad' },
        ],
        'analitica': [
            { label: 'Tendencias', path: '/analitica' },
            { label: 'Análisis RFC', path: '/analitica/rfc' },
            { label: 'Riesgo Cartera', path: '/analitica/cartera' },
            { label: 'Patrones', path: '/analitica/patrones' },
        ]
    };

    const isUUIDPath = ['/', '/detalle-uuid', '/trazabilidad'].includes(location.pathname);
    const isAnaliticaPath = location.pathname.startsWith('/analitica');

    // Strictly show for 'cuenta-t' module and relevant paths
    if (activeModule !== 'cuenta-t' || (!isUUIDPath && !isAnaliticaPath)) return null;

    const items = isUUIDPath ? moduleConfig['uuid'] : moduleConfig['analitica'];

    const handleTabClick = (path) => {
        setActiveSubTab(activeModule, path);
        navigate(path);
    };

    return (
        <div className="bg-white border-b border-slate-200 px-8 py-3 flex items-center gap-8 overflow-x-auto no-scrollbar">
            {items.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                    <button
                        key={item.path}
                        onClick={() => handleTabClick(item.path)}
                        className={`whitespace-nowrap px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 ${isActive
                            ? 'bg-[#7c5cbf] text-white shadow-md transform scale-105'
                            : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                            }`}
                    >
                        {item.label}
                    </button>
                );
            })}
        </div>
    );
};

export default SubTabNav;
