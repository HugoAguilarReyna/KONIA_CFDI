import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle, XCircle, BarChart2, ShieldAlert } from 'lucide-react';
import dashboardService from '../dashboard/dashboardService';
import KPICard from '../../components/ui/KPICard';
import ChartWrapper from '../../components/ui/ChartWrapper';
import { motion } from 'framer-motion';

const RiskView = () => {
    const { uuid } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            if (!uuid) return;
            setLoading(true);
            try {
                const result = await dashboardService.getRiskAnalysis(uuid);
                if (result.error) {
                    setError(result.error);
                } else {
                    setData(result);
                }
            } catch (err) {
                setError("Error al cargar análisis de riesgos.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [uuid]);

    if (loading) return <div className="p-8 text-center text-slate-500 font-mono text-xs uppercase tracking-widest">ANALIZANDO RIESGOS...</div>;

    if (error) return (
        <div className="p-8 text-center bg-white border border-slate-200 rounded-xl max-w-2xl mx-auto shadow-sm">
            <p className="text-red-500 font-bold mb-4 uppercase text-sm">{error}</p>
            <button onClick={() => navigate(-1)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-bold flex items-center justify-center gap-2 mx-auto transition-colors">
                <ArrowLeft size={16} /> VOLVER
            </button>
        </div>
    );

    if (!data) return null;

    // Determine Risk Level Color
    const riskLevel = data.risk_score > 70 ? 'danger' : data.risk_score > 30 ? 'warning' : 'success';
    const riskColor = data.risk_score > 70 ? '#ef4444' : data.risk_score > 30 ? '#f59e0b' : '#10b981';

    // Gauge Chart Data
    const gaugeData = [
        {
            type: "indicator",
            mode: "gauge+number",
            value: data.risk_score,
            title: { text: "NIVEL DE RIESGO", font: { size: 16, family: 'monospace', color: '#64748b' } },
            number: { font: { color: '#1e293b', size: 40 } },
            gauge: {
                axis: { range: [null, 100], tickwidth: 1, tickcolor: "#64748b" },
                bar: { color: riskColor },
                bgcolor: "#f8fafc",
                borderwidth: 0,
                steps: [
                    { range: [0, 30], color: "#d1fae5" },
                    { range: [30, 70], color: "#fef3c7" },
                    { range: [70, 100], color: "#fee2e2" }
                ],
            }
        }
    ];

    return (
        <div className="space-y-8 max-w-6xl mx-auto pb-10">
            {/* Header */}
            <div className="flex items-center gap-4 border-b border-slate-200 pb-4">
                <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                    <ArrowLeft size={20} />
                </button>
                <div className="flex flex-col">
                    <h1 className="text-xl font-bold font-mono text-slate-800 tracking-tight uppercase flex items-center gap-2">
                        <ShieldAlert className={data.risk_score > 30 ? 'text-amber-500' : 'text-indigo-600'} />
                        ANÁLISIS FORENSE DE RIESGOS
                    </h1>
                    <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
                        {data.uuid}
                    </div>
                </div>
            </div>

            {/* Top Section: Score & Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Gauge Chart Card */}
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col items-center justify-center">
                    <ChartWrapper
                        type="plotly"
                        data={gaugeData}
                        layout={{
                            margin: { t: 40, b: 20, l: 30, r: 30 },
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                        }}
                        height={250}
                        isLoading={loading}
                        config={{ displayModeBar: false }}
                    />
                </div>

                {/* Flags Grid Card */}
                <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
                    <h3 className="text-xs font-bold font-mono text-slate-400 uppercase tracking-widest mb-6 border-b border-slate-50 pb-2">INDICADORES ESTRATÉGICOS</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <FlagItem
                            label="MONTO REDONDO"
                            status={data.flags.round_number}
                            description="Probable estimación o manipulación de cifras."
                        />
                        <FlagItem
                            label="HORARIO ATÍPICO"
                            status={data.flags.atypical_hour}
                            description="Emisión fuera de ventana operativa estándar."
                        />
                        <FlagItem
                            label="WEEKEND BILLING"
                            status={data.flags.weekend_billing}
                            description="Facturación en días no laborables."
                        />
                        <FlagItem
                            label="DESVIACIÓN EST."
                            status={data.flags.mean_deviation}
                            description="Supera significativamente el promedio histórico."
                        />
                    </div>
                </div>
            </div>

            {/* Metrics Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <KPICard
                    title="MONTO DOCUMENTO"
                    value={`$${parseFloat(data.metrics.total).toLocaleString('es-MX', { minimumFractionDigits: 2 })}`}
                    icon={BarChart2}
                    color="primary"
                    variant="simple"
                />
                <KPICard
                    title="PROMEDIO HISTÓRICO"
                    value={`$${parseFloat(data.metrics.emisor_avg).toLocaleString('es-MX', { minimumFractionDigits: 2 })}`}
                    icon={Activity}
                    color="info"
                    variant="simple"
                />
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center">
                <p className="text-xs text-slate-500 font-mono uppercase tracking-widest">
                    El score de riesgo es una métrica probabilística basada en patrones históricos y no constituye una prueba legal por sí misma.
                </p>
            </div>
        </div>
    );
};

const FlagItem = ({ label, status, description }) => (
    <div className={`p-4 rounded-lg border flex items-start gap-4 transition-all duration-300 ${status ? 'bg-red-50 border-red-200 shadow-sm' : 'bg-white border-slate-100'}`}>
        <div className={`mt-0.5 p-1.5 rounded-full ${status ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
            {status ? <XCircle size={18} /> : <CheckCircle size={18} />}
        </div>
        <div>
            <p className={`font-bold text-xs font-mono uppercase tracking-tight ${status ? 'text-red-700' : 'text-slate-700'}`}>{label}</p>
            <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">{description}</p>
        </div>
    </div>
);

export default RiskView;
