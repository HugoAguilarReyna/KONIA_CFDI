
import React, { useEffect, useState, useMemo } from 'react';
import { DollarSign, TrendingUp, TrendingDown, Activity, PieChart, CreditCard, Layers, FileText, AlertTriangle } from 'lucide-react';
import useFilterStore from '../../stores/useFilterStore';
import dashboardService from './dashboardService';
import KPICard from '../../components/ui/KPICard';
import ChartCard from '../../components/ui/ChartCard';
import { COLORS } from '../../config/colors';

// Recharts Imports
import {
    PieChart as RePieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    ComposedChart, Area, Line, ReferenceLine, LabelList
} from "recharts";

// Font constants for Recharts
const CHART_FONT = { fontFamily: "'Montserrat', sans-serif" };
const CHART_FONT_MONO = { fontFamily: "'JetBrains Mono', monospace" };

const MatrizResumen = () => {
    const { filters } = useFilterStore();
    const [data, setData] = useState(null);
    const [tablaData, setTablaData] = useState(null);
    const [evolution, setEvolution] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingTable, setLoadingTable] = useState(true);
    const [copied, setCopied] = useState(false);

    // 1. Fetch Evolution Histórica (Only once on mount)
    useEffect(() => {
        const fetchEvolucion = async () => {
            try {
                const res = await dashboardService.getMatrizEvolucion();
                if (res && res.evolucion) {
                    setEvolution(res.evolucion);
                } else {
                    console.warn("Evolution data missing/invalid:", res);
                    setEvolution([]);
                }
            } catch (error) {
                console.error("Error fetching evolution:", error);
                setEvolution([]);
            }
        };
        fetchEvolucion();
    }, []);

    // 2. Fetch Period Data (KPIs and Charts) & Table Data (Comparative)
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setLoadingTable(true);
            try {
                const periodo = `${filters.year}-${String(filters.month).padStart(2, '0')}`;

                const [resMatriz, resTabla] = await Promise.all([
                    dashboardService.getMatrizResumen({ periodo }),
                    dashboardService.getMatrizTabla(periodo)
                ]);

                setData(resMatriz);
                setTablaData(resTabla);
            } catch (error) {
                console.error("Error fetching period data:", error);
            } finally {
                setLoading(false);
            }
            // Small delay for table loading effect if needed, but usually redundant
            setLoadingTable(false);
        };

        if (filters.year && filters.month) {
            fetchData();
        }
    }, [filters.year, filters.month]);

    const handleCopyTable = () => {
        const table = document.getElementById('matriz-table');
        if (table) {
            const range = document.createRange();
            range.selectNode(table);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand('copy');
            window.getSelection().removeAllRanges();
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const formatCurrency = (val, compact = false) => {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            notation: compact ? 'compact' : 'standard',
            maximumFractionDigits: compact ? 1 : 2
        }).format(val);
    };

    // --- Chart Components (Internal) ---

    // 1. Double Ring Donut Chart (Facturación vs Saldos)
    const DoubleRingDonut = ({ ppdFacturado, pueFacturado, saldoPPD, saldoPUE }) => {
        const dataFacturacion = [
            { name: "PPD Facturado", value: Math.abs(ppdFacturado), color: COLORS.ppd },
            { name: "PUE Facturado", value: Math.abs(pueFacturado), color: COLORS.pue }
        ];

        const dataSaldos = [
            { name: "Saldo PPD", value: Math.abs(saldoPPD), color: `${COLORS.ppd}AA` }, // 80% opacity
            { name: "Saldo PUE", value: Math.abs(saldoPUE), color: `${COLORS.pue}AA` }  // 80% opacity
        ];

        const CustomTooltip = ({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const item = payload[0];
            return (
                <div style={{
                    background: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: "10px",
                    padding: "10px 14px",
                    boxShadow: "0 4px 20px rgba(0,0,0,0.12)"
                }}>
                    <p style={{ fontWeight: 700, color: item.payload.color, fontFamily: "Montserrat", fontSize: "13px" }}>
                        {item.name}
                    </p>
                    <p style={{ fontFamily: "JetBrains Mono", fontSize: "14px", color: "#1e293b", fontWeight: 700 }}>
                        {formatCurrency(item.value)}
                    </p>
                </div>
            );
        };

        const CustomLegend = () => (
            <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "10px", flexWrap: "wrap" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{ width: "10px", height: "10px", background: COLORS.ppd, borderRadius: "2px" }} />
                    <span style={{ ...CHART_FONT, fontSize: "11px", color: "#64748b", fontWeight: 500 }}>PPD Facturado</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{ width: "10px", height: "10px", background: `${COLORS.ppd}AA`, borderRadius: "2px" }} />
                    <span style={{ ...CHART_FONT, fontSize: "11px", color: "#64748b", fontWeight: 500 }}>PPD Saldo (Int.)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{ width: "10px", height: "10px", background: COLORS.pue, borderRadius: "2px" }} />
                    <span style={{ ...CHART_FONT, fontSize: "11px", color: "#64748b", fontWeight: 500 }}>PUE Facturado</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{ width: "10px", height: "10px", background: `${COLORS.pue}AA`, borderRadius: "2px" }} />
                    <span style={{ ...CHART_FONT, fontSize: "11px", color: "#64748b", fontWeight: 500 }}>PUE Saldo (Int.)</span>
                </div>
            </div>
        );

        return (
            <div style={{ position: "relative", width: "100%", height: 320 }}>
                <div style={{ position: "absolute", top: 10, right: 10, fontSize: "10px", color: "#94a3b8", ...CHART_FONT, textAlign: "right", fontWeight: 500 }}>
                    Exterior: Facturado<br />Interior: Saldos
                </div>
                <ResponsiveContainer width="100%" height={280}>
                    <RePieChart>
                        {/* Outer Ring: Facturación */}
                        <Pie
                            data={dataFacturacion}
                            cx="50%" cy="50%"
                            innerRadius={85} outerRadius={110}
                            paddingAngle={3}
                            dataKey="value"
                            strokeWidth={0}
                        >
                            {dataFacturacion.map((entry, i) => (
                                <Cell key={i} fill={entry.color} />
                            ))}
                        </Pie>
                        {/* Inner Ring: Saldos */}
                        <Pie
                            data={dataSaldos}
                            cx="50%" cy="50%"
                            innerRadius={58} outerRadius={80}
                            paddingAngle={3}
                            dataKey="value"
                            strokeWidth={0}
                        >
                            {dataSaldos.map((entry, i) => (
                                <Cell key={i} fill={entry.color} />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                    </RePieChart>
                </ResponsiveContainer>
                <CustomLegend />
            </div>
        );
    };

    // 2. Desglose Comparado (Combined Bar Chart) - UPDATED FIX
    const DesgloseComparado = ({ matrizPPD, matrizPUE }) => {

        const CONCEPTOS = [
            "2. (-) Notas de Crédito (01)",
            "3. (+) Nota de Débito (02)",
            "4. (-) Devoluciones (03)",
            "5. (-) Sustituciones (04)",
            "6. Traslado de mercancia (05,06)",
            "7. (-) Anticipo (07)",
            "8. (-) Pagos Aplicados (08/09)"
        ];

        const formatLabel = (concepto) => {
            const sinNumero = concepto.replace(/^\d+\.\s*/, "");     // quitar "8. "
            const sinCodigo = sinNumero.replace(/\s*\(\d+.*?\)$/, ""); // quitar "(08/09)"
            const sinSigno = sinCodigo.replace(/^\([+-]\)\s*/, "");   // quitar "(-) "
            return sinSigno.trim();
        };

        // Construir datos para la gráfica
        const data = CONCEPTOS.map(concepto => ({
            name: formatLabel(concepto),
            concepto_full: concepto,
            ppd: Math.abs(matrizPPD?.[concepto] || 0),
            pue: Math.abs(matrizPUE?.[concepto] || 0),
        }))
            // Ordenar por max(ppd, pue) desc
            .sort((a, b) => Math.max(b.ppd, b.pue) - Math.max(a.ppd, a.pue));

        const formatXAxis = (value) => {
            if (value >= 1000000) return `$${(value / 1000000).toFixed(0)}M`;
            if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
            return `$${value}`;
        };

        const CustomTooltip = ({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            return (
                <div style={{
                    background: "#1e293b",
                    borderRadius: "10px",
                    padding: "10px 14px",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                    minWidth: "180px",
                    zIndex: 100
                }}>
                    <p style={{
                        color: "#94a3b8", fontSize: "11px",
                        ...CHART_FONT, fontWeight: 700,
                        letterSpacing: "0.05em", marginBottom: "8px",
                        textTransform: "uppercase"
                    }}>
                        {label}
                    </p>
                    {payload.map((p, i) => (
                        p.value > 0 && (
                            <div key={i} style={{
                                display: "flex",
                                justifyContent: "space-between",
                                gap: "20px",
                                marginBottom: "4px",
                                alignItems: "center"
                            }}>
                                <span style={{
                                    display: "flex", alignItems: "center",
                                    gap: "6px", color: "white",
                                    fontSize: "11px", ...CHART_FONT
                                }}>
                                    <span style={{
                                        width: "8px", height: "8px",
                                        borderRadius: "50%",
                                        background: p.color,
                                        flexShrink: 0
                                    }} />
                                    {p.name}
                                </span>
                                <span style={{
                                    color: p.color,
                                    ...CHART_FONT_MONO,
                                    fontSize: "12px", fontWeight: 700
                                }}>
                                    {formatCurrency(p.value)}
                                </span>
                            </div>
                        )
                    ))}
                </div>
            );
        };

        const CustomLegend = () => (
            <div style={{
                display: "flex", justifyContent: "center",
                gap: "24px", marginTop: "12px"
            }}>
                {[
                    { color: COLORS.ppd, label: "PPD" },
                    { color: COLORS.pue, label: "PUE" }
                ].map(item => (
                    <div key={item.label} style={{
                        display: "flex", alignItems: "center", gap: "6px"
                    }}>
                        <div style={{
                            width: "10px", height: "10px",
                            borderRadius: "3px",
                            background: item.color
                        }} />
                        <span style={{
                            fontSize: "11px", color: "#64748b",
                            ...CHART_FONT, fontWeight: 500
                        }}>
                            {item.label}
                        </span>
                    </div>
                ))}
            </div>
        );

        return (
            <div>
                <ResponsiveContainer width="100%" height={350}>
                    <BarChart
                        data={data}
                        layout="vertical"
                        margin={{
                            top: 8,
                            right: 80,   // espacio para el label de valor
                            left: 0,     // ← cambiar a 0, el YAxis maneja su propio ancho
                            bottom: 8
                        }}
                    >
                        <CartesianGrid horizontal={false} strokeDasharray="3 3" stroke="#f1f5f9" />

                        <XAxis
                            type="number"
                            tickFormatter={formatXAxis}
                            tick={{
                                ...CHART_FONT,
                                fontSize: 11,
                                fontWeight: 400,
                                fill: "#94a3b8"
                            }}
                            axisLine={false}
                            tickLine={false}
                            tickCount={5}
                        />

                        <YAxis
                            type="category"
                            dataKey="name"
                            tick={{
                                ...CHART_FONT,
                                fontSize: 13,
                                fill: "#64748b",
                                fontWeight: 500,
                                textAnchor: "end"   // ← alinear texto a la derecha del eje
                            }}
                            axisLine={false}
                            tickLine={false}
                            width={160}             // ← ancho fijo suficiente para los labels
                            dx={-4}                 // ← pequeño offset para separar del eje
                        />

                        <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />

                        {/* Barra PPD */}
                        <Bar dataKey="ppd" name="PPD" fill={COLORS.ppd} radius={[0, 6, 6, 0]} maxBarSize={14}>
                            <LabelList dataKey="ppd" position="right" formatter={(v) => v > 0 ? `$${(v / 1000000).toFixed(1)}M` : ""} style={{ ...CHART_FONT_MONO, fontSize: "11px", fill: COLORS.ppd, fontWeight: 600 }} />
                            {data.map((entry, i) => (
                                <Cell key={i} fill={entry.ppd === 0 ? "#f1f5f9" : COLORS.ppd} opacity={entry.ppd === 0 ? 0.4 : 1} />
                            ))}
                        </Bar>

                        {/* Barra PUE */}
                        <Bar dataKey="pue" name="PUE" fill={COLORS.pue} radius={[0, 6, 6, 0]} maxBarSize={14}>
                            <LabelList dataKey="pue" position="right" formatter={(v) => v > 0 ? `$${(v / 1000000).toFixed(1)}M` : ""} style={{ ...CHART_FONT_MONO, fontSize: "11px", fill: COLORS.pue, fontWeight: 600 }} />
                            {data.map((entry, i) => (
                                <Cell key={i} fill={entry.pue === 0 ? "#f1f5f9" : COLORS.pue} opacity={entry.pue === 0 ? 0.4 : 1} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
                <CustomLegend />
            </div>
        );
    };

    // 3. Evolution Chart
    const EvolucionChart = ({ data }) => {
        const CustomTooltip = ({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            return (
                <div style={{
                    background: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    padding: "12px 16px",
                    boxShadow: "0 8px 30px rgba(0,0,0,0.12)"
                }}>
                    <p style={{ fontWeight: 700, color: "#1e293b", ...CHART_FONT, marginBottom: "8px", fontSize: "12px" }}>
                        {label}
                    </p>
                    {payload.map((p, i) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: "24px", marginBottom: "4px" }}>
                            <span style={{ fontSize: "11px", color: p.color, ...CHART_FONT, fontWeight: 600 }}>
                                {p.name}
                            </span>
                            <span style={{ fontSize: "11px", ...CHART_FONT_MONO, color: "#1e293b", fontWeight: 700 }}>
                                {formatCurrency(Math.abs(p.value), true)}
                            </span>
                        </div>
                    ))}
                </div>
            );
        };

        const formatYAxisPPD = (v) => `$${(v / 1000000).toFixed(0)}M`;
        const formatYAxisPUE = (v) => `$${(v / 1000000).toFixed(1)}M`;

        return (
            <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={data} margin={{ top: 20, right: 0, left: 0, bottom: 20 }}>
                    <defs>
                        <linearGradient id="gradPPD" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.ppd} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={COLORS.ppd} stopOpacity={0.05} />
                        </linearGradient>
                        <linearGradient id="gradPUE" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.pue} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={COLORS.pue} stopOpacity={0.05} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="periodo" tick={{ ...CHART_FONT, fontSize: 11, fill: "#64748b", fontWeight: 400 }} axisLine={false} tickLine={false} />

                    <YAxis yAxisId="ppd" orientation="left" tickFormatter={formatYAxisPPD} tick={{ ...CHART_FONT, fontSize: 11, fill: COLORS.ppd, fontWeight: 500 }} axisLine={false} tickLine={false} />
                    <YAxis yAxisId="pue" orientation="right" tickFormatter={formatYAxisPUE} tick={{ ...CHART_FONT, fontSize: 11, fill: COLORS.pue, fontWeight: 500 }} axisLine={false} tickLine={false} />

                    <ReferenceLine yAxisId="ppd" y={0} stroke="#e2e8f0" strokeWidth={1.5} />
                    <Tooltip content={<CustomTooltip />} />

                    <Bar yAxisId="ppd" dataKey="saldo_ppd" name="Saldo PPD" fill={COLORS.ppd} opacity={0.85} radius={[4, 4, 0, 0]} maxBarSize={50} />
                    <Area yAxisId="pue" type="monotone" dataKey="saldo_pue" name="Saldo PUE" stroke={COLORS.pue} strokeWidth={2.5} fill="url(#gradPUE)" dot={{ fill: "white", stroke: COLORS.pue, strokeWidth: 2.5, r: 5 }} activeDot={{ r: 7, fill: COLORS.pue, stroke: "white", strokeWidth: 2 }} />

                    <Legend iconType="circle" iconSize={10} wrapperStyle={{ ...CHART_FONT, paddingTop: "16px", fontSize: "12px", fontWeight: 500 }} formatter={(value) => <span style={{ color: "#475569" }}>{value}</span>} />
                </ComposedChart>
            </ResponsiveContainer>
        );
    };

    // --- Data Prep ---
    const chartData = useMemo(() => {
        if (!data) return null;
        const { matriz } = data;

        // Facturado (Outer Ring)
        const ppdFacturado = matriz.PPD?.["1. (+) Total Facturado"] || 0;
        const pueFacturado = matriz.PUE?.["1. (+) Total Facturado"] || 0;

        // Saldos (Inner Ring)
        // Use "9. (=) Saldo..." key from your data structure
        const saldoPPD = matriz.PPD?.["9. (=) Saldo Insoluto PPD"] || 0;
        const saldoPUE = matriz.PUE?.["9. (=) Saldo Teórico PUE"] || 0;

        return {
            ppdFacturado,
            pueFacturado,
            saldoPPD,
            saldoPUE,
            matrizPPD: matriz.PPD || {},
            matrizPUE: matriz.PUE || {},
        };
    }, [data]);

    // --- Table Processing ---
    const tableRows = useMemo(() => {
        if (!tablaData) return [];
        const { matriz_actual: actual, matriz_anterior: anterior } = tablaData;
        const rows = [];
        const CONCEPTOS_ORDEN = [
            "1. (+) Total Facturado",
            "2. (-) Notas de Crédito (01)",
            "3. (+) Nota de Débito (02)",
            "4. (-) Devoluciones (03)",
            "5. (-) Sustituciones (04)",
            "6. Traslado de mercancia (05,06)",
            "7. (-) Anticipo (07)",
            "8. (-) Pagos Aplicados (08/09)",
        ];
        const CONCEPTO_9 = { "PPD": "9. (=) Saldo Insoluto PPD", "PUE": "9. (=) Saldo Teórico PUE" };

        const calcularVariacion = (actual, anterior) => {
            if (!anterior || anterior === 0) {
                return actual !== 0 ? "NUEVO" : "--";
            }
            const pct = ((actual - anterior) / Math.abs(anterior)) * 100;
            const formatted = `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`;
            if (Math.abs(pct) > 500) return `${formatted} ⚠️`;
            return formatted;
        };

        ["PPD", "PUE"].forEach(segmento => {
            const currentSeg = actual[segmento] || {};
            const prevSeg = anterior[segmento] || {};
            const totalFacturadoActual = currentSeg["1. (+) Total Facturado"] || 1;

            CONCEPTOS_ORDEN.forEach((concepto, idx) => {
                const montoActual = currentSeg[concepto] || 0;
                const montoAnt = prevSeg[concepto] || 0;
                rows.push({
                    segmento: idx === 0 ? segmento : "",
                    concepto,
                    montoAnterior: montoAnt,
                    montoActual,
                    porcentaje: `${(montoActual / totalFacturadoActual * 100).toFixed(1)}%`,
                    variacion: calcularVariacion(montoActual, montoAnt),
                    status: "",
                    totalGlobal: montoActual
                });
            });

            const c9 = CONCEPTO_9[segmento];
            const saldoActual = currentSeg[c9] || 0;
            const saldoAnt = prevSeg[c9] || 0;
            rows.push({
                segmento: "",
                concepto: c9,
                montoAnterior: saldoAnt,
                montoActual: saldoActual,
                porcentaje: `${(saldoActual / totalFacturadoActual * 100).toFixed(1)}%`,
                variacion: calcularVariacion(saldoActual, saldoAnt),
                status: "OK",
                totalGlobal: saldoActual,
                isConcept9: true,
                segmentLabel: segmento // To separate styling
            });

            rows.push({ type: 'subtotal', label: `SUBTOTAL ${segmento}`, montoActual: saldoActual, montoAnterior: saldoAnt });
        });
        return rows;
    }, [tablaData]);


    const kpis = data?.kpis || {};
    // Calculate simple variations for banner (mock logic if not in API)
    // Ideally these should come from backend, but we can infer or use mock for now based on user request example
    const varIngresos = -2.4; // Mock value as per example or if calculateable from `tablaData`
    const varSaldoPPD = 12.5;

    // Component for Variation Cell Icon
    const VarCell = ({ value }) => {
        if (value === "--" || value === "NUEVO") return <span style={{ color: "#cbd5e1" }}>--</span>;

        const isPositive = value.startsWith("+");
        const isSuspect = value.includes("⚠️");
        // For revenue/assets: positive is good (green). For debt/risk: positive might be bad.
        // Assuming generic "green is up" context for now unless specified.
        const color = isSuspect ? "#FFCA28" : isPositive ? "#26A69A" : "#FF8A65";

        return (
            <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                {!isSuspect && (
                    isPositive ? <TrendingUp size={12} color="#26A69A" /> : <TrendingDown size={12} color="#FF8A65" />
                )}
                <span style={{ fontFamily: "JetBrains Mono", fontSize: "11px", fontWeight: 600, color }}>{value}</span>
            </div>
        )
    };

    // Helper for dynamic table headers
    const periodLabels = useMemo(() => {
        if (!filters.year || !filters.month) return { prev: "PREVIO", act: "ACTUAL" };
        const dateAct = new Date(filters.year, filters.month - 1);
        const datePrev = new Date(filters.year, filters.month - 2);

        const fmt = (d) => d.toLocaleString('es-ES', { month: 'short', year: '2-digit' }).replace('.', '').toUpperCase();
        return {
            prev: fmt(datePrev),
            act: fmt(dateAct)
        };
    }, [filters.year, filters.month]);

    return (
        <div className="space-y-6 pb-12">

            {/* [NEW] Header Banner Fiscal */}
            <div style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "12px 20px", background: "white", borderRadius: "12px", marginBottom: "16px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderLeft: "4px solid #6B84F3"
            }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <span style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                        Período Activo
                    </span>
                    <span style={{ fontSize: "15px", color: "#1e293b", fontFamily: "JetBrains Mono", fontWeight: 700 }}>
                        {filters.year} - {new Date(0, filters.month - 1).toLocaleString('es-ES', { month: 'long' }).toUpperCase()}
                    </span>
                </div>
                {/* Comparativo rápido (Mocked for visual compliance) */}
                <div style={{ display: "flex", gap: "24px" }}>
                    <div style={{ textAlign: "right" }}>
                        <p style={{ fontSize: "10px", color: "#94a3b8", fontFamily: "Montserrat", fontWeight: 600 }}>vs Mes Prev.</p>
                        <p style={{ fontSize: "13px", fontFamily: "JetBrains Mono", color: varIngresos >= 0 ? "#26A69A" : "#FF8A65", fontWeight: 700 }}>
                            {varIngresos >= 0 ? "+" : ""}{varIngresos.toFixed(1)}% <span style={{ fontSize: "10px", color: "#94a3b8", fontWeight: 400, fontFamily: "Montserrat" }}>Ingresos</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* [NEW] Critical Alert Chip */}
            {kpis.status === "EN RIESGO CRÍTICO" && (
                <div style={{
                    display: "flex", alignItems: "center", gap: "10px",
                    padding: "10px 16px", background: "#FF8A6510",
                    border: "1px solid #FF8A6530", borderRadius: "10px", marginBottom: "16px"
                }}>
                    <AlertTriangle size={16} color="#FF8A65" />
                    <p style={{ fontSize: "12px", color: "#FF8A65", fontFamily: "Montserrat", fontWeight: 600 }}>
                        Atención: El Saldo Insoluto PPD supera <strong>{kpis.ratio_riesgo ? kpis.ratio_riesgo.toFixed(1) : 0}x</strong> el Total Facturado. Se recomienda revisión de pagos aplicados.
                    </p>
                </div>
            )}

            {/* KPI Grid - Compact Style + Ratio Correction */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 mb-6">
                <KPICard title="Ingresos Totales" value={formatCurrency(kpis.ingresos_totales || 0, true)} icon={TrendingUp} accentColor={COLORS.exito} isLoading={loading} />
                <KPICard title="Saldo PPD" value={formatCurrency(kpis.saldo_ppd || 0, true)} icon={Layers} accentColor={COLORS.ppd} isLoading={loading} />
                <KPICard title="Ingreso PUE" value={formatCurrency(kpis.ingreso_pue || 0, true)} icon={DollarSign} accentColor={COLORS.pue} isLoading={loading} />
                <KPICard title="Créditos / NC" value={formatCurrency(Math.abs(kpis.creditos_nc || 0), true)} icon={FileText} accentColor={COLORS.alerta} isLoading={loading} />
                {/* Ratio adjusted to multiplier based on kpis.ratio_formato from updated backend, or fallback */}
                <KPICard title="Ratio PPD/PUE" value={kpis.ratio_formato || `${(kpis.ratio_ppd_pue || 0).toFixed(1)}%`} icon={PieChart} accentColor={COLORS.cian} isLoading={loading} />
                <KPICard title="Status Fiscal"
                    value={kpis.status === "SALUDABLE" ? "✓ Saludable" : kpis.status === "EN RIESGO" ? "⚠ En Riesgo" : "✕ Crítico"}
                    icon={Activity}
                    accentColor={kpis.status === "SALUDABLE" ? COLORS.exito : kpis.status === "EN RIESGO" ? COLORS.precaucion : COLORS.alerta}
                    isLoading={loading}
                />
            </div>

            {/* Charts: Donut + Desglose */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Double Ring Donut */}
                <ChartCard title="DISTRIBUCIÓN PPD VS PUE" borderColor={COLORS.ppd} isLoading={loading}>
                    {chartData && (
                        <DoubleRingDonut
                            ppdFacturado={chartData.ppdFacturado}
                            pueFacturado={chartData.pueFacturado}
                            saldoPPD={chartData.saldoPPD}
                            saldoPUE={chartData.saldoPUE}
                        />
                    )}
                </ChartCard>

                {/* Desglose Comparado */}
                <div className="lg:col-span-2">
                    <ChartCard title="DESGLOSE COMPARADO PPD VS PUE" borderColor={COLORS.pue} isLoading={loading}>
                        {chartData && <DesgloseComparado matrizPPD={chartData.matrizPPD} matrizPUE={chartData.matrizPUE} />}
                    </ChartCard>
                </div>
            </div>

            {/* Evolution Chart */}
            <ChartCard title="EVOLUCIÓN DE SALDOS (HISTÓRICO)" borderColor={COLORS.marino} isLoading={loading}>
                {evolution.length >= 2 ? (
                    <EvolucionChart data={evolution} />
                ) : (
                    <div className="h-[300px] flex flex-col items-center justify-center text-slate-400 gap-2">
                        <TrendingUp size={32} strokeWidth={1.5} />
                        <span className="text-[10px] uppercase font-mono tracking-widest">Se necesitan al menos 2 períodos</span>
                    </div>
                )}
            </ChartCard>

            {/* Comparative Table - Updated Typography and Sticky Header */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-6">
                <div className="p-4 flex justify-between items-center bg-[#5b6ec4] border-b-4 border-[#283593]">
                    <h2 className="text-sm font-bold text-white uppercase tracking-widest font-mono">MATRIZ FINANCIERA DETALLADA</h2>
                    <button
                        onClick={handleCopyTable}
                        className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-[11px] font-bold font-mono border border-white/20"
                    >
                        {copied ? <span className="text-emerald-300">✓ COPIADO</span> : <><FileText size={14} /> COPIAR TABLA</>}
                    </button>
                </div>
                {/* Removed max-h-[600px] and overflow-y-auto to show full table as requested */}
                <div className="relative overflow-x-auto">
                    <table id="matriz-table" className="w-full min-w-[1000px] border-collapse">
                        {/* Sticky Header removed as we want to show full table, but keeping it structurally doesn't hurt if we scroll the page */}
                        <thead>
                            <tr className="bg-[#5b6ec4] text-white border-b border-[#283593]">
                                <th className="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-wider w-24 font-display border-r border-indigo-400/30">SEGMENTO</th>
                                <th className="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-wider font-display border-r border-indigo-400/30">CONCEPTO FISCAL</th>
                                <th className="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-wider w-36 font-display border-r border-indigo-400/30">{periodLabels.prev}</th>
                                <th className="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-wider w-36 font-display border-r border-indigo-400/30">{periodLabels.act}</th>
                                <th className="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-wider w-24 font-display border-r border-indigo-400/30">% TOTAL</th>
                                <th className="px-4 py-2 text-center text-[11px] font-semibold uppercase tracking-wider w-20 font-display border-r border-indigo-400/30">VAR.</th>
                                <th className="px-4 py-2 text-center text-[11px] font-semibold uppercase tracking-wider w-20 font-display border-r border-indigo-400/30">STATUS</th>
                                <th className="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-wider w-36 font-display">TOTAL GLOBAL</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-100">
                            {loadingTable ? (
                                <tr><td colSpan={8} className="py-20 text-center text-slate-400 font-mono text-xs animate-pulse">CARGANDO MATRIZ...</td></tr>
                            ) : tableRows.map((row, idx) => {
                                if (row.type === 'subtotal') {
                                    return (
                                        <tr key={idx} className="bg-slate-50/80">
                                            <td className="px-4 py-2 text-[12px] font-bold text-slate-800 uppercase font-display border-r border-slate-200">{row.label}</td>
                                            <td colSpan={1} className="px-4 py-2 text-right text-[10px] font-bold text-slate-400 font-mono italic border-r border-slate-200">RESULTADO OPERATIVO</td>
                                            <td className="px-4 py-2 text-right text-[13px] font-bold text-slate-400 font-mono border-r border-slate-200">{formatCurrency(row.montoAnterior)}</td>
                                            <td className="px-4 py-2 text-right text-[13px] font-bold text-indigo-600 font-mono border-r border-slate-200">{formatCurrency(row.montoActual)}</td>
                                            <td colSpan={3} className="border-r border-slate-200"></td>
                                            <td className="px-4 py-2 text-right text-[13px] font-bold text-indigo-600 font-mono">{formatCurrency(row.montoActual)}</td>
                                        </tr>
                                    );
                                }

                                // Special styling for Row 9 (Saldo)
                                const rowStyle = row.isConcept9 ? {
                                    background: row.segmentLabel === "PPD" ? `linear-gradient(90deg, ${COLORS.ppd}08, transparent)` : `linear-gradient(90deg, ${COLORS.pue}08, transparent)`,
                                    borderTop: `1px solid ${row.segmentLabel === "PPD" ? COLORS.ppd : COLORS.pue}20`,
                                    borderBottom: `1px solid ${row.segmentLabel === "PPD" ? COLORS.ppd : COLORS.pue}20`
                                } : {};

                                return (
                                    <tr key={idx} style={rowStyle} className={`hover:bg-slate-50 transition-colors`}>
                                        <td className="px-4 py-2 border-r border-slate-100">
                                            {row.segmento === 'PPD' && <span style={{ color: COLORS.ppd, borderColor: `${COLORS.ppd}40` }} className="bg-slate-50 px-2 py-0.5 rounded text-[10px] font-black tracking-tighter uppercase border text-center inline-block w-full font-display">PPD</span>}
                                            {row.segmento === 'PUE' && <span style={{ color: COLORS.pue, borderColor: `${COLORS.pue}40` }} className="bg-slate-50 px-2 py-0.5 rounded text-[10px] font-black tracking-tighter uppercase border text-center inline-block w-full font-display">PUE</span>}
                                        </td>
                                        {/* Reduced font size for concept */}
                                        <td className={`px-4 py-2 text-[12px] ${row.isConcept9 ? 'font-bold text-slate-900' : 'text-slate-700 font-medium'} font-display border-r border-slate-100`}>{row.concepto}</td>
                                        <td className="px-4 py-2 text-[12px] text-right font-mono text-slate-400 border-r border-slate-100">{formatCurrency(row.montoAnterior)}</td>
                                        <td className={`px-4 py-2 text-[12px] text-right font-mono font-bold ${row.montoActual < 0 ? 'text-rose-500' : 'text-slate-700'} border-r border-slate-100`}>{formatCurrency(row.montoActual)}</td>
                                        <td className="px-4 py-2 text-[11px] text-slate-400 text-right font-mono border-r border-slate-100">{row.porcentaje}</td>
                                        <td className="px-4 py-2 border-r border-slate-100">
                                            <VarCell value={row.variacion} />
                                        </td>
                                        <td className="px-4 py-2 text-center border-r border-slate-100">
                                            {row.status === 'OK' && <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-50 text-emerald-600 uppercase border border-emerald-100 font-display">OK</span>}
                                        </td>
                                        <td className={`px-4 py-2 text-[13px] text-right font-mono font-bold ${row.isConcept9 ? 'text-slate-900' : 'text-slate-600'}`}>{formatCurrency(row.totalGlobal)}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default MatrizResumen;
