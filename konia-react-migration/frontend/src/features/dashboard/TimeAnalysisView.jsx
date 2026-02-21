import React, { useEffect, useState, useMemo } from 'react';
import { BarChart, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import useFilterStore from '../../stores/useFilterStore';
import dashboardService from './dashboardService';
import KPICard from '../../components/ui/KPICard';
import ChartWrapper from '../../components/ui/ChartWrapper';
import DataTable from '../../components/ui/DataTable';
import { createColumnHelper } from '@tanstack/react-table';

const TimeAnalysisView = () => {
    const { filters } = useFilterStore();
    const [data, setData] = useState({ breakdown: [], kpis: {} });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Construct period YYYY-MM
                let periodo = filters.periodo;
                if (!periodo && filters.year && filters.month) {
                    periodo = `${filters.year}-${filters.month.toString().padStart(2, '0')}`;
                }

                // Fallback to default if no period
                if (!periodo) periodo = '2024-01'; // Should be dynamic ideally

                const result = await dashboardService.getDimTiempo(periodo);
                setData(result);
            } catch (error) {
                console.error("Error fetching time analysis:", error);
                // Mock data in case of error (since endpoint might not return what we expect if empty)
                setData({ breakdown: [], kpis: {} });
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [filters.year, filters.month, filters.periodo]);

    // --- Chart Data ---
    const chartData = useMemo(() => {
        if (!data.breakdown || data.breakdown.length === 0) return [];
        // Map breakdown to Stacked Bar
        // X: Periodo, Y: Ingreso, Egreso, Nomina
        return [
            {
                x: data.breakdown.map(d => d.periodo),
                y: data.breakdown.map(d => d.ingreso),
                name: 'Ingreso',
                type: 'bar',
                marker: { color: '#10b981' }
            },
            {
                x: data.breakdown.map(d => d.periodo),
                y: data.breakdown.map(d => d.egreso),
                name: 'Egreso',
                type: 'bar',
                marker: { color: '#ef4444' }
            },
            {
                x: data.breakdown.map(d => d.periodo),
                y: data.breakdown.map(d => d.nomina),
                name: 'Nómina',
                type: 'bar',
                marker: { color: '#f59e0b' }
            }
        ];
    }, [data.breakdown]);

    // --- Table Config ---
    const columnHelper = createColumnHelper();
    const columns = useMemo(() => [
        columnHelper.accessor('periodo', {
            header: 'PERIODO',
            cell: info => <span className="font-bold text-slate-700">{info.getValue()}</span>,
            size: 100
        }),
        columnHelper.accessor('ingreso', {
            header: 'INGRESO',
            cell: info => <span className="font-mono text-green-600 font-bold text-right block">${(info.getValue() || 0).toLocaleString()}</span>,
            size: 120
        }),
        columnHelper.accessor('egreso', {
            header: 'EGRESO',
            cell: info => <span className="font-mono text-red-600 font-bold text-right block">${(info.getValue() || 0).toLocaleString()}</span>,
            size: 120
        }),
        columnHelper.accessor('nomina', {
            header: 'NÓMINA',
            cell: info => <span className="font-mono text-orange-600 font-bold text-right block">${(info.getValue() || 0).toLocaleString()}</span>,
            size: 120
        }),
        columnHelper.accessor('resultado', {
            header: 'RESULTADO',
            cell: info => (
                <span className={`font-mono font-bold text-right block ${info.getValue() >= 0 ? 'text-indigo-600' : 'text-red-500'}`}>
                    ${(info.getValue() || 0).toLocaleString()}
                </span>
            ),
            size: 120
        })
    ], []);

    return (
        <div className="space-y-8 pb-10">
            {/* Header */}
            <div className="flex flex-col gap-1 border-b border-slate-200 pb-4">
                <h1 className="text-xl font-bold font-mono text-slate-800 tracking-tight uppercase">ANÁLISIS TEMPORAL</h1>
                <div className="w-16 h-1 bg-indigo-600 rounded-full"></div>
                <p className="text-slate-500 text-xs mt-1">Comparativa mensual de flujos financieros.</p>
            </div>

            {/* Chart */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
                <h3 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">
                    EVOLUCIÓN MENSUAL (INGRESOS / EGRESOS / NÓMINA)
                </h3>
                <ChartWrapper
                    type="plotly"
                    data={chartData}
                    isLoading={loading}
                    layout={{
                        barmode: 'stack', // Stacked bars
                        margin: { t: 20, b: 40, l: 60, r: 20 },
                        height: 400,
                        xaxis: { title: 'Periodo' },
                        yaxis: { title: 'Monto ($)', tickprefix: '$' },
                        legend: { orientation: 'h', y: 1.1 }
                    }}
                />
            </div>

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <div className="bg-slate-50 px-6 py-3 border-b border-slate-200">
                    <h3 className="text-xs font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
                        <BarChart size={14} className="text-indigo-600" />
                        DETALLE POR PERIODO
                    </h3>
                </div>
                <DataTable
                    data={data.breakdown || []}
                    columns={columns}
                    isLoading={loading}
                    height={400}
                />
            </div>
        </div>
    );
};

export default TimeAnalysisView;
