import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Download, Filter, Activity, FileText, DollarSign, Calculator, PieChart as PieChartIcon, GitBranch, X, AlertTriangle, CheckCircle, Check, Copy } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, LabelList, ScatterChart, Scatter, ZAxis, CartesianGrid, ReferenceLine } from 'recharts';
import useFilterStore from '../../stores/useFilterStore';
import useUIStore from '../../stores/useUIStore';
import { useTrazabilidadStore } from '../../stores/useTrazabilidadStore';
import dashboardService from './dashboardService';
import KPICard from '../../components/ui/KPICard';
import ChartCard from '../../components/ui/ChartCard';


const CustomBarHistogram = (props) => {
    const { x, y, width, height, count } = props
    return (
        <g>
            <rect x={x} y={y} width={width} height={height}
                rx={4} ry={4}
                fill="#6B84F3" fillOpacity={0.85} />
            {height > 20 && (
                <text x={x + width / 2} y={y - 5}
                    textAnchor="middle"
                    fontSize={10}
                    fontFamily="JetBrains Mono"
                    fill="#6B84F3"
                    fontWeight={700}>
                    {count}
                </text>
            )}
        </g>
    )
}

const DetalleUUIDView = () => {
    const { filters } = useFilterStore();
    const navigate = useNavigate();
    const { setActiveSubTab } = useUIStore();
    const { setUUIDTrazabilidad } = useTrazabilidadStore();

    const [data, setData] = useState({
        registros: [],
        kpis: { total_uuids: 0, saldo_total: 0, promedio_saldo: 0, ratio_emit_recib: 0 },
        distribucion: {},
        top10: [],
        total: 0
    });
    const [loading, setLoading] = useState(true);
    const [searchUUID, setSearchUUID] = useState('');
    const [copiedUUID, setCopiedUUID] = useState(null);

    const handleCopyUUID = (uuid) => {
        navigator.clipboard.writeText(uuid);
        setCopiedUUID(uuid);
        setTimeout(() => setCopiedUUID(null), 2000);
    };

    const [filtros, setFiltros] = useState({
        segmento: null,
        flujo: null,
        saldo_min: 0,
        page: 1,
        limit: 25
    });

    const nombreMes = filters.month ? new Date(2026, filters.month - 1).toLocaleString('es-MX', { month: 'long' }) : 'Mes';
    const anio = filters.year || 'Año';

    const handleClearAll = () => {
        setSearchUUID('');
        setFiltros({
            ...filtros,
            segmento: null,
            flujo: null,
            saldo_min: 0,
            page: 1
        });
    };

    const hasFilters = searchUUID !== '' || filtros.segmento !== null || filtros.flujo !== null || filtros.saldo_min > 0;

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                let periodo = filters.periodo;
                if (!periodo && filters.year && filters.month) {
                    periodo = `${filters.year}-${filters.month.toString().padStart(2, '0')}`;
                }

                const result = await dashboardService.getDetalleUUID(
                    periodo,
                    filtros.page,
                    filtros.limit,
                    {
                        flujo: filtros.flujo,
                        segmento: filtros.segmento,
                        saldo_min: filtros.saldo_min,
                        uuid_search: searchUUID
                    }
                );

                setData({
                    registros: result.registros || [],
                    kpis: result.kpis || { total_uuids: 0, saldo_total: 0, promedio_saldo: 0, ratio_emit_recib: 0 },
                    distribucion: result.distribucion || {},
                    top10: result.top10 || [],
                    total: result.total || 0
                });
            } catch (error) {
                console.error("Error fetching detail data:", error);
            } finally {
                setLoading(false);
            }
        };

        const debounceTimeout = setTimeout(() => {
            fetchData();
        }, 300);

        return () => clearTimeout(debounceTimeout);
    }, [filters.year, filters.month, filtros, searchUUID]);

    const formatMoney = (amount, compact = false) => {
        if (compact && amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
        if (compact && amount >= 1000) return `$${(amount / 1000).toFixed(1)}k`;
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            maximumFractionDigits: 2
        }).format(amount);
    };

    const handleExportCSV = () => {
        const headers = [
            "UUID", "SEGMENTO", "FLUJO",
            "1. (+) Total Facturado",
            "2. (-) Notas de Crédito (01)",
            "4. (-) Devoluciones (03)",
            "7. (-) Anticipo (07)",
            "8. (-) Pagos Aplicados (08/09)",
            "9. (=) Saldo Acumulado"
        ];
        const rows = data.registros.map(doc => [
            doc.uuid,
            doc.segmento,
            doc.flujo,
            doc.conceptos?.["1. (+) Total Facturado"] ?? 0,
            doc.conceptos?.["2. (-) Notas de Crédito (01)"] ?? 0,
            doc.conceptos?.["4. (-) Devoluciones (03)"] ?? 0,
            doc.conceptos?.["7. (-) Anticipo (07)"] ?? 0,
            doc.conceptos?.["8. (-) Pagos Aplicados (08/09)"] ?? 0,
            doc.saldo_acumulado
        ]);
        const csv = [headers, ...rows]
            .map(r => r.join(","))
            .join("\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `detalle_uuid_${filters.periodo || ''}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const kpis = data.kpis;
    const registros = data.registros;
    const total = data.total;

    // Scatter Data
    const ScatterRiesgo = ({ scatterData, formatMoney }) => {
        const [tooltipVisible, setTooltipVisible] = useState(true);

        // Calcular rangos reales de los datos
        const todosLosPuntos = [
            ...scatterData.PUE,
            ...scatterData.PPD,
            ...scatterData.OTROS
        ];
        const maxX = Math.max(...todosLosPuntos.map(d => d.x), 0) * 1.1 || 1000;
        const maxY = Math.max(...todosLosPuntos.map(d => Math.abs(d.y)), 0) * 1.1 || 1000;
        const minY = Math.min(...todosLosPuntos.map(d => d.y), 0) * 1.1 || -100;

        const CustomTooltipScatter = ({ active, payload, onClose }) => {
            if (!active || !payload?.length) return null
            const d = payload[0]?.payload
            if (!d) return null

            const sinPagos = Math.abs(d.y - d.x) < d.x * 0.05
                && Math.abs(d.y) > 0.01
            const liquidado = Math.abs(d.y) < 0.01

            const handleIrADetalle = () => {
                setSearchUUID(d.uuid)
                const tableEl = document.getElementById("tabla-auditoria")
                if (tableEl) tableEl.scrollIntoView({ behavior: "smooth" })
            }

            return (
                <div style={{
                    background: "white",
                    borderRadius: "20px",
                    padding: "24px 28px",
                    minWidth: "360px",
                    boxShadow: `
                        0 0 0 1px rgba(0,0,0,0.06),
                        0 8px 24px rgba(0,0,0,0.10),
                        0 24px 64px rgba(0,0,0,0.12)
                    `,
                    border: "none",
                    pointerEvents: "all",
                    position: "relative"
                }}>
                    {/* Botón Cerrar (X) */}
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onClose();
                        }}
                        style={{
                            position: "absolute",
                            top: "16px",
                            right: "16px",
                            background: "#f1f5f9",
                            border: "none",
                            borderRadius: "50%",
                            width: "28px",
                            height: "28px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            color: "#94a3b8",
                            zIndex: 10,
                            transition: "all 0.2s"
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = "#e2e8f0"}
                        onMouseLeave={e => e.currentTarget.style.background = "#f1f5f9"}
                    >
                        <X size={16} strokeWidth={2.5} />
                    </button>

                    {/* UUID + Badge segmento en misma fila */}
                    <div style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        marginBottom: "16px",
                        gap: "12px",
                        paddingRight: "20px" // Espacio para la X
                    }}>
                        <p style={{
                            fontFamily: "JetBrains Mono",
                            fontSize: "12px",
                            color: "#94a3b8",
                            lineHeight: 1.6,
                            wordBreak: "break-all",
                            flex: 1
                        }}>
                            {d.uuid}
                        </p>

                        {/* Badge segmento */}
                        <span style={{
                            padding: "4px 14px",
                            borderRadius: "20px",
                            fontSize: "11px",
                            fontFamily: "Montserrat",
                            fontWeight: 800,
                            letterSpacing: "0.06em",
                            flexShrink: 0,
                            background:
                                d.segmento === "PUE" ? "#6B84F315" :
                                    d.segmento === "PPD" ? "#78579915" :
                                        "#CBD0DA30",
                            color:
                                d.segmento === "PUE" ? "#6B84F3" :
                                    d.segmento === "PPD" ? "#785799" :
                                        "#94a3b8"
                        }}>
                            {d.segmento}
                        </span>
                    </div>

                    {/* Separador */}
                    <div style={{
                        height: "1px",
                        background: "#f1f5f9",
                        marginBottom: "16px"
                    }} />

                    {/* Valores principales — más grandes */}
                    <div style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "16px",
                        marginBottom: "16px"
                    }}>
                        <div>
                            <p style={{
                                fontSize: "10px",
                                color: "#94a3b8",
                                fontFamily: "Montserrat",
                                fontWeight: 700,
                                textTransform: "uppercase",
                                letterSpacing: "0.08em",
                                marginBottom: "6px"
                            }}>
                                Facturado
                            </p>
                            <p style={{
                                fontFamily: "JetBrains Mono",
                                fontSize: "26px",
                                fontWeight: 700,
                                color: "#26A69A",
                                lineHeight: 1
                            }}>
                                {formatMoney(d.x, true)}
                            </p>
                        </div>
                        <div>
                            <p style={{
                                fontSize: "10px",
                                color: "#94a3b8",
                                fontFamily: "Montserrat",
                                fontWeight: 700,
                                textTransform: "uppercase",
                                letterSpacing: "0.08em",
                                marginBottom: "6px"
                            }}>
                                Saldo Acum.
                            </p>
                            <p style={{
                                fontFamily: "JetBrains Mono",
                                fontSize: "26px",
                                fontWeight: 700,
                                color: d.y >= 0 ? "#6B84F3" : "#FF8A65",
                                lineHeight: 1
                            }}>
                                {formatMoney(d.y, true)}
                            </p>
                        </div>
                    </div>

                    {/* Alerta fiscal */}
                    {(sinPagos || liquidado) && (
                        <div style={{
                            padding: "10px 14px",
                            borderRadius: "12px",
                            marginBottom: "16px",
                            background: liquidado
                                ? "#26A69A10" : "#FF8A6510",
                            border: `1px solid ${liquidado ? "#26A69A30" : "#FF8A6530"
                                }`,
                            display: "flex",
                            alignItems: "center",
                            gap: "8px"
                        }}>
                            {liquidado
                                ? <CheckCircle size={15} color="#26A69A" />
                                : <AlertTriangle size={15} color="#FF8A65" />
                            }
                            <p style={{
                                fontSize: "12px",
                                fontFamily: "Montserrat",
                                fontWeight: 700,
                                color: liquidado ? "#26A69A" : "#FF8A65"
                            }}>
                                {liquidado
                                    ? "Completamente liquidado"
                                    : "Sin pagos aplicados"}
                            </p>
                        </div>
                    )}

                    {/* Separador */}
                    <div style={{
                        height: "1px",
                        background: "#f1f5f9",
                        marginBottom: "16px"
                    }} />

                    {/* Botones de acción */}
                    <div style={{ display: "flex", gap: "10px" }}>

                        {/* Copiar UUID */}
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleCopyUUID(d.uuid);
                            }}
                            style={{
                                padding: "10px 16px",
                                borderRadius: "12px",
                                border: "1px solid #e2e8f0",
                                cursor: "pointer",
                                background: copiedUUID === d.uuid
                                    ? "#26A69A10" : "white",
                                color: copiedUUID === d.uuid
                                    ? "#26A69A" : "#64748b",
                                fontFamily: "Montserrat",
                                fontSize: "12px",
                                fontWeight: 700,
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                transition: "all 0.2s",
                                flexShrink: 0
                            }}
                        >
                            {copiedUUID === d.uuid
                                ? <><Check size={13} /> Copiado</>
                                : <><Copy size={13} /> Copiar</>
                            }
                        </button>

                        {/* Ver en Tabla */}
                        <button
                            onClick={handleIrADetalle}
                            style={{
                                flex: 1,
                                padding: "10px 16px",
                                borderRadius: "12px",
                                border: "1px solid #e2e8f0",
                                cursor: "pointer",
                                background: "white",
                                color: "#1e293b",
                                fontFamily: "Montserrat",
                                fontSize: "12px",
                                fontWeight: 700,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: "6px",
                                transition: "all 0.2s"
                            }}
                            onMouseEnter={e =>
                                e.currentTarget.style.background = "#f8fafc"}
                            onMouseLeave={e =>
                                e.currentTarget.style.background = "white"}
                        >
                            <Search size={13} />
                            Tabla
                        </button>

                        {/* Trazabilidad */}
                        <button
                            onClick={() => {
                                setActiveSubTab("trazabilidad-uuid")
                                setUUIDTrazabilidad(d.uuid)
                                navigate('/trazabilidad')
                            }}
                            style={{
                                flex: 1,
                                padding: "10px 16px",
                                borderRadius: "12px",
                                border: "none",
                                cursor: "pointer",
                                background: "#6B84F3",
                                color: "white",
                                fontFamily: "Montserrat",
                                fontSize: "12px",
                                fontWeight: 700,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: "6px",
                                transition: "opacity 0.2s"
                            }}
                            onMouseEnter={e =>
                                e.currentTarget.style.opacity = "0.85"}
                            onMouseLeave={e =>
                                e.currentTarget.style.opacity = "1"}
                        >
                            <GitBranch size={13} />
                            Trazabilidad
                        </button>
                    </div>
                </div>
            )
        }

        const CustomLegend = () => (
            <div style={{
                display: "flex",
                justifyContent: "center",
                gap: "24px",
                marginTop: "16px",
                paddingTop: "12px",
                borderTop: "1px solid #f1f5f9"
            }}>
                {[
                    { color: "#6B84F3", label: "PUE", count: scatterData.PUE.length },
                    { color: "#785799", label: "PPD", count: scatterData.PPD.length },
                    { color: "#CBD0DA", label: "OTROS", count: scatterData.OTROS.length },
                ].map(item => (
                    <div key={item.label} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: item.color }} />
                        <span style={{ fontFamily: "Montserrat", fontSize: "12px", color: "#64748b", fontWeight: 500 }}>{item.label}</span>
                        <span style={{ fontFamily: "JetBrains Mono", fontSize: "11px", color: "#94a3b8" }}>({item.count})</span>
                    </div>
                ))}
                <div style={{ width: "1px", background: "#e2e8f0", margin: "0 8px" }} />
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{ width: "20px", height: "1px", background: "#FF8A65", borderTop: "1px dashed #FF8A65" }} />
                    <span style={{ fontFamily: "Montserrat", fontSize: "11px", color: "#FF8A65", fontWeight: 500 }}>Sin pagos (y=x)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{ width: "20px", height: "1px", borderTop: "1px dashed #26A69A" }} />
                    <span style={{ fontFamily: "Montserrat", fontSize: "11px", color: "#26A69A", fontWeight: 500 }}>Liquidación (y=0)</span>
                </div>
            </div>
        )

        return (
            <div style={{ width: "100%", height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 40, left: 70, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis
                            type="number"
                            dataKey="x"
                            name="Facturado"
                            domain={[0, maxX]}
                            tickFormatter={v => v >= 1000000 ? `$${(v / 1000000).toFixed(1)}M` : `$${(v / 1000).toFixed(0)}k`}
                            tick={{ fontSize: 10, fontFamily: "Montserrat", fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                            label={{ value: "Total Facturado", position: "insideBottom", offset: -8, fontSize: 10, fontFamily: "Montserrat", fill: "#64748b" }}
                        />
                        <YAxis
                            type="number"
                            dataKey="y"
                            name="Saldo"
                            domain={[minY, maxY]}
                            tickFormatter={v => v >= 1000000 ? `$${(v / 1000000).toFixed(1)}M` : `$${(v / 1000).toFixed(0)}k`}
                            tick={{ fontSize: 10, fontFamily: "Montserrat", fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                            label={{ value: "Saldo Acumulado", angle: -90, position: "insideLeft", offset: 10, fontSize: 10, fontFamily: "Montserrat", fill: "#64748b" }}
                        />
                        <ZAxis type="number" dataKey="z" range={[40, 400]} />
                        <ReferenceLine segment={[{ x: 0, y: 0 }, { x: maxX, y: maxX }]} stroke="#FF8A65" strokeWidth={1} strokeDasharray="6 4" strokeOpacity={0.5} ifOverflow="extendDomain" />
                        <ReferenceLine y={0} stroke="#26A69A" strokeWidth={1.5} strokeDasharray="6 4" strokeOpacity={0.6} label={{ value: "← Liquidación", position: "insideLeft", fontSize: 9, fontFamily: "Montserrat", fill: "#26A69A", fontWeight: 700 }} />
                        <Tooltip
                            content={<CustomTooltipScatter onClose={() => setTooltipVisible(false)} />}
                            active={tooltipVisible ? undefined : false}
                            trigger="click"
                            wrapperStyle={{ pointerEvents: "all" }}
                            cursor={{ strokeDasharray: "3 3", stroke: "#e2e8f0" }}
                        />
                        <Scatter
                            name="PUE"
                            data={scatterData.PUE}
                            fill="#6B84F3"
                            fillOpacity={0.75}
                            stroke="white"
                            strokeWidth={1.5}
                            onClick={() => setTooltipVisible(true)}
                        />
                        <Scatter
                            name="PPD"
                            data={scatterData.PPD}
                            fill="#785799"
                            fillOpacity={0.75}
                            stroke="white"
                            strokeWidth={1.5}
                            onClick={() => setTooltipVisible(true)}
                        />
                        <Scatter
                            name="OTROS"
                            data={scatterData.OTROS}
                            fill="#CBD0DA"
                            fillOpacity={0.75}
                            stroke="white"
                            strokeWidth={1.5}
                            onClick={() => setTooltipVisible(true)}
                        />
                    </ScatterChart>
                </ResponsiveContainer>
                <CustomLegend />
            </div>
        );
    };
    const scatterData = {
        PUE: registros.filter(r => r.segmento === "PUE").map(r => ({
            x: r.conceptos?.["1. (+) Total Facturado"] || 0,
            y: r.saldo_acumulado,
            z: Math.max(30, Math.abs(r.saldo_acumulado)),
            uuid: r.uuid,
            segmento: r.segmento
        })),
        PPD: registros.filter(r => r.segmento === "PPD").map(r => ({
            x: r.conceptos?.["1. (+) Total Facturado"] || 0,
            y: r.saldo_acumulado,
            z: Math.max(30, Math.abs(r.saldo_acumulado)),
            uuid: r.uuid,
            segmento: r.segmento
        })),
        OTROS: registros.filter(r => r.segmento === "OTROS").map(r => ({
            x: r.conceptos?.["1. (+) Total Facturado"] || 0,
            y: r.saldo_acumulado,
            z: Math.max(30, Math.abs(r.saldo_acumulado)),
            uuid: r.uuid,
            segmento: r.segmento
        }))
    };
    const maxFact = Math.max(...registros.map(r => r.conceptos?.["1. (+) Total Facturado"] || 0), 0);

    // Waterfall Data
    const calcularWaterfall = (registros) => {
        const totales = {
            facturado: 0,
            notas: 0,
            devoluciones: 0,
            anticipo: 0,
            pagos: 0,
            saldo: 0
        };
        registros.forEach(r => {
            totales.facturado += r.conceptos?.["1. (+) Total Facturado"] || 0;
            totales.notas += r.conceptos?.["2. (-) Notas de Crédito (01)"] || 0;
            totales.devoluciones += r.conceptos?.["4. (-) Devoluciones (03)"] || 0;
            totales.anticipo += r.conceptos?.["7. (-) Anticipo (07)"] || 0;
            totales.pagos += r.conceptos?.["8. (-) Pagos Aplicados (08/09)"] || 0;
            totales.saldo += r.saldo_acumulado;
        });

        let acumulado = totales.facturado;
        return [
            {
                name: "Total\nFacturado",
                valor: totales.facturado,
                base: 0,
                color: "#26A69A",
                tipo: "positivo"
            },
            {
                name: "Notas de\nCrédito",
                valor: Math.abs(totales.notas),
                base: acumulado + totales.notas,
                color: "#FF8A65",
                tipo: "negativo",
                _acum: (acumulado += totales.notas)
            },
            {
                name: "Devoluciones",
                valor: Math.abs(totales.devoluciones),
                base: acumulado + totales.devoluciones,
                color: "#FF8A65",
                tipo: "negativo",
                _acum: (acumulado += totales.devoluciones)
            },
            {
                name: "Anticipo",
                valor: Math.abs(totales.anticipo),
                base: acumulado + totales.anticipo,
                color: "#FFCA28",
                tipo: "negativo",
                _acum: (acumulado += totales.anticipo)
            },
            {
                name: "Pagos\nAplicados",
                valor: Math.abs(totales.pagos),
                base: acumulado + totales.pagos,
                color: "#FFCA28",
                tipo: "negativo",
                _acum: (acumulado += totales.pagos)
            },
            {
                name: "Saldo\nNeto",
                valor: Math.abs(totales.saldo),
                base: 0,
                color: totales.saldo >= 0 ? "#6B84F3" : "#ef4444",
                tipo: "resultado"
            }
        ];
    };
    const waterfallData = calcularWaterfall(registros);

    return (
        <div style={{ paddingBottom: "40px" }}>
            {/* Header */}
            <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: "24px",
                padding: "20px 24px",
                background: "white",
                borderRadius: "16px",
                borderLeft: "4px solid #6B84F3",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
            }}>
                {/* Izquierda */}
                <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                        <h2 style={{
                            fontSize: "20px",
                            fontFamily: "Montserrat",
                            fontWeight: 800,
                            color: "#1e293b",
                            letterSpacing: "0.05em",
                            textTransform: "uppercase",
                            margin: 0
                        }}>
                            Explorador de Registros UUID
                        </h2>
                    </div>
                    <p style={{
                        fontSize: "13px",
                        fontFamily: "Montserrat",
                        color: "#94a3b8",
                        fontWeight: 400,
                        margin: 0
                    }}>
                        Gestión detallada de folios fiscales y auditoría documental
                        — Período: <strong style={{ color: "#6B84F3", textTransform: 'capitalize' }}>
                            {nombreMes} {anio}
                        </strong>
                    </p>
                </div>

                {/* Derecha: Buscar + Exportar */}
                <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                    <div style={{
                        display: "flex", alignItems: "center", gap: "8px",
                        background: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        borderRadius: "10px",
                        padding: "8px 14px",
                        width: "260px"
                    }}>
                        <Search size={15} color="#94a3b8" />
                        <input
                            placeholder="Buscar UUID, RFC..."
                            value={searchUUID}
                            onChange={e => setSearchUUID(e.target.value)}
                            style={{
                                border: "none", background: "transparent",
                                fontFamily: "Montserrat", fontSize: "13px",
                                color: "#1e293b", outline: "none",
                                flex: 1, minWidth: 0
                            }}
                        />
                        {searchUUID && (
                            <button
                                onClick={() => setSearchUUID('')}
                                style={{
                                    background: "#f1f5f9",
                                    border: "none",
                                    borderRadius: "50%",
                                    width: "22px",
                                    height: "22px",
                                    cursor: "pointer",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    color: "#64748b",
                                    transition: "all 0.2s",
                                    boxShadow: "0 1px 2px rgba(0,0,0,0.05)"
                                }}
                                onMouseEnter={e => {
                                    e.currentTarget.style.background = "#fee2e2";
                                    e.currentTarget.style.color = "#ef4444";
                                }}
                                onMouseLeave={e => {
                                    e.currentTarget.style.background = "#f1f5f9";
                                    e.currentTarget.style.color = "#64748b";
                                }}
                                title="Limpiar búsqueda"
                            >
                                <X size={12} strokeWidth={3} />
                            </button>
                        )}
                    </div>

                    {hasFilters && (
                        <button
                            onClick={handleClearAll}
                            style={{
                                display: "flex", alignItems: "center", gap: "6px",
                                background: "#fff1f2", color: "#e11d48",
                                border: "1px solid #fda4af", borderRadius: "10px",
                                padding: "9px 16px", cursor: "pointer",
                                fontFamily: "Montserrat", fontSize: "12px",
                                fontWeight: 800, transition: "all 0.2s",
                                boxShadow: "0 2px 4px rgba(225, 29, 72, 0.1)"
                            }}
                            onMouseEnter={e => {
                                e.currentTarget.style.background = "#e11d48";
                                e.currentTarget.style.color = "white";
                            }}
                            onMouseLeave={e => {
                                e.currentTarget.style.background = "#fff1f2";
                                e.currentTarget.style.color = "#e11d48";
                            }}
                        >
                            <X size={14} strokeWidth={2.5} />
                            LIMPIAR FILTROS
                        </button>
                    )}
                    <button
                        onClick={handleExportCSV}
                        style={{
                            display: "flex", alignItems: "center", gap: "8px",
                            background: "#6B84F3", color: "white",
                            border: "none", borderRadius: "10px",
                            padding: "9px 18px", cursor: "pointer",
                            fontFamily: "Montserrat", fontSize: "13px",
                            fontWeight: 700
                        }}
                    >
                        <Download size={15} />
                        EXPORTAR
                    </button>
                </div>
            </div>

            {/* KPI Cards */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "16px",
                marginBottom: "24px"
            }}>
                <KPICard
                    title="Total UUIDs"
                    value={kpis.total_uuids.toLocaleString("es-MX")}
                    icon={FileText}
                    accentColor="#6B84F3"
                    isLoading={loading}
                />
                <KPICard
                    title="Saldo Total"
                    value={formatMoney(kpis.saldo_total, true)}
                    icon={DollarSign}
                    accentColor="#26A69A"
                    isLoading={loading}
                />
                <KPICard
                    title="Promedio Op."
                    value={formatMoney(kpis.promedio_saldo, true)}
                    icon={Calculator}
                    accentColor="#FF8A65"
                    isLoading={loading}
                />
                <KPICard
                    title="Ratio Emit/Recib"
                    value={`${kpis.ratio_emit_recib.toFixed(1)}%`}
                    icon={PieChartIcon}
                    accentColor="#785799"
                    isLoading={loading}
                />
            </div>

            {/* Fila 1: Filtros (izquierda) + Waterfall (derecha) */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "280px 1fr",
                gap: "16px",
                marginBottom: "16px"
            }}>
                {/* Panel filtros */}
                <div style={{
                    background: "white",
                    borderRadius: "16px",
                    padding: "20px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
                }}>
                    <p style={{
                        fontSize: "14px", fontFamily: "Montserrat",
                        fontWeight: 700, color: "#1e293b",
                        display: "flex", alignItems: "center", gap: "8px",
                        margin: "0 0 20px 0"
                    }}>
                        <Filter size={15} color="#6B84F3" />
                        Filtros de Negocio
                    </p>

                    <label style={{
                        display: "block", fontSize: "10px", fontFamily: "Montserrat",
                        fontWeight: 700, color: "#94a3b8",
                        letterSpacing: "0.08em", textTransform: "uppercase"
                    }}>
                        Segmento Operativo
                    </label>
                    <select
                        value={filtros.segmento || ""}
                        onChange={e => setFiltros(p => ({
                            ...p, segmento: e.target.value || null, page: 1
                        }))}
                        style={{
                            width: "100%", marginTop: "6px", marginBottom: "16px",
                            padding: "9px 12px", borderRadius: "8px",
                            border: "1px solid #e2e8f0",
                            fontFamily: "Montserrat", fontSize: "13px",
                            color: "#1e293b", background: "white", cursor: "pointer",
                            outline: "none"
                        }}
                    >
                        <option value="">Todos los Segmentos</option>
                        <option value="PUE">PUE</option>
                        <option value="PPD">PPD</option>
                        <option value="OTROS">OTROS</option>
                    </select>

                    <label style={{
                        display: "block", fontSize: "10px", fontFamily: "Montserrat",
                        fontWeight: 700, color: "#94a3b8",
                        letterSpacing: "0.08em", textTransform: "uppercase"
                    }}>
                        Flujo de Caja
                    </label>
                    <select
                        value={filtros.flujo || ""}
                        onChange={e => setFiltros(p => ({
                            ...p, flujo: e.target.value || null, page: 1
                        }))}
                        style={{
                            width: "100%", marginTop: "6px", marginBottom: "16px",
                            padding: "9px 12px", borderRadius: "8px",
                            border: "1px solid #e2e8f0",
                            fontFamily: "Montserrat", fontSize: "13px",
                            color: "#1e293b", background: "white", cursor: "pointer",
                            outline: "none"
                        }}
                    >
                        <option value="">Todos</option>
                        <option value="EMITIDOS">EMITIDOS</option>
                        <option value="RECIBIDOS">RECIBIDOS</option>
                    </select>

                    <label style={{
                        display: "block", fontSize: "10px", fontFamily: "Montserrat",
                        fontWeight: 700, color: "#94a3b8",
                        letterSpacing: "0.08em", textTransform: "uppercase"
                    }}>
                        Rango de Saldo Mínimo
                    </label>
                    <input
                        type="range" min={0} max={500000} step={1000}
                        value={filtros.saldo_min || 0}
                        onChange={e => setFiltros(p => ({
                            ...p, saldo_min: Number(e.target.value) || null, page: 1
                        }))}
                        style={{
                            width: "100%", marginTop: "8px",
                            accentColor: "#6B84F3"
                        }}
                    />
                    <div style={{
                        display: "flex", justifyContent: "space-between",
                        marginTop: "4px"
                    }}>
                        <span style={{
                            fontSize: "10px", color: "#94a3b8",
                            fontFamily: "Montserrat"
                        }}>
                            MIN: ${(filtros.saldo_min || 0).toLocaleString("es-MX")}
                        </span>
                        <span style={{
                            fontSize: "10px", color: "#94a3b8",
                            fontFamily: "Montserrat"
                        }}>
                            MAX: 500k+
                        </span>
                    </div>
                </div>

                {/* Waterfall */}
                <ChartCard
                    title="WATERFALL — COMPOSICIÓN DEL SALDO AGREGADO"
                    borderColor="#26A69A"
                    subtitle="Cómo llega del facturado al saldo neto"
                >
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart
                            data={waterfallData}
                            margin={{ top: 30, right: 20, left: 80, bottom: 20 }}
                        >
                            <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis
                                dataKey="name"
                                tick={{
                                    fontSize: 10, fontFamily: "Montserrat",
                                    fill: "#64748b", whiteSpace: "pre-line"
                                }}
                                axisLine={false} tickLine={false}
                            />
                            <YAxis
                                tickFormatter={v => `$${(Math.abs(v) / 1000000).toFixed(1)}M`}
                                tick={{ fontSize: 10, fontFamily: "JetBrains Mono", fill: "#94a3b8" }}
                                axisLine={false} tickLine={false}
                            />
                            <Tooltip
                                formatter={(v, name, props) => {
                                    if (name === "base") return null
                                    const d = props.payload
                                    return [
                                        formatMoney(d.tipo === "negativo" ? -v : v),
                                        d.name.replace("\n", " ")
                                    ]
                                }}
                                contentStyle={{ fontFamily: "Montserrat", borderRadius: "10px" }}
                            />

                            {/* Barra invisible de base */}
                            <Bar dataKey="base" stackId="wf" fill="transparent" legendType="none" />

                            {/* Barra visible de valor */}
                            <Bar dataKey="valor" stackId="wf" radius={[6, 6, 0, 0]} maxBarSize={60}>
                                {waterfallData.map((entry, i) => (
                                    <Cell key={i} fill={entry.color}
                                        fillOpacity={
                                            entry.tipo === "negativo" ? 0.8 :
                                                entry.tipo === "resultado" ? 1 : 0.9
                                        } />
                                ))}
                                <LabelList
                                    dataKey="valor"
                                    position="top"
                                    formatter={(v, i) => {
                                        const entry = waterfallData[i]
                                        if (!entry) return ""
                                        const prefix = entry.tipo === "negativo" ? "-" : ""
                                        return `${prefix}${formatMoney(v, true)}`
                                    }}
                                    style={{
                                        fontSize: "10px",
                                        fontFamily: "JetBrains Mono",
                                        fontWeight: 700,
                                        fill: "#475569"
                                    }}
                                />
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            {/* Fila 2: Scatter ancho completo */}
            <div style={{ marginBottom: "16px" }}>
                <ChartCard
                    title="FACTURADO VS SALDO — DETECCIÓN DE RIESGO"
                    borderColor="#6B84F3"
                    subtitle={
                        <span style={{
                            fontSize: "11px",
                            fontFamily: "Montserrat",
                            color: "#94a3b8"
                        }}>
                            Cada punto = 1 UUID &nbsp;·&nbsp;
                            Tamaño proporcional al saldo &nbsp;·&nbsp;
                            <span style={{ color: "#FF8A65" }}>
                                Diagonal = sin pagos aplicados
                            </span>
                        </span>
                    }
                >
                    <ScatterRiesgo scatterData={scatterData} formatMoney={formatMoney} />
                </ChartCard>
            </div>

            {/* TABLA EXPLORADOR */}
            <div id="tabla-auditoria" style={{
                background: "white",
                marginTop: "16px",
                borderRadius: "16px",
                overflow: "hidden",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
            }}>
                <div style={{
                    display: "flex", justifyContent: "space-between",
                    alignItems: "center",
                    padding: "16px 24px",
                    borderBottom: "1px solid #f1f5f9"
                }}>
                    <p style={{
                        fontSize: "13px", fontFamily: "Montserrat",
                        fontWeight: 700, color: "#1e293b",
                        display: "flex", alignItems: "center", gap: "8px",
                        margin: 0
                    }}>
                        <Activity size={15} color="#6B84F3" />
                        Auditoría de Documentos Fiscales
                    </p>
                    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <span style={{
                            fontSize: "12px", color: "#94a3b8",
                            fontFamily: "Montserrat"
                        }}>
                            {total.toLocaleString("es-MX")} registros encontrados
                        </span>
                        <select
                            value={filtros.limit}
                            onChange={e => setFiltros(p => ({
                                ...p, limit: Number(e.target.value), page: 1
                            }))}
                            style={{
                                padding: "6px 10px", borderRadius: "8px",
                                border: "1px solid #e2e8f0",
                                fontFamily: "Montserrat", fontSize: "12px",
                                color: "#1e293b", cursor: "pointer",
                                outline: "none"
                            }}
                        >
                            <option value={25}>25 por pág.</option>
                            <option value={50}>50 por pág.</option>
                            <option value={100}>100 por pág.</option>
                        </select>
                    </div>
                </div>

                <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr style={{ background: "#f8fafc" }}>
                                {[
                                    { label: "UUID", width: "220px" },
                                    { label: "SEGMENTO", width: "90px" },
                                    { label: "FLUJO", width: "90px" },
                                    { label: "1. (+) TOTAL\nFACTURADO", width: "120px" },
                                    { label: "2. (-) NOTAS DE\nCRÉDITO (01)", width: "120px" },
                                    { label: "4. (-)\nDEVOLUCIONES (03)", width: "110px" },
                                    { label: "7. (-)\nANTICIPO (07)", width: "100px" },
                                    { label: "8. (-) PAGOS\nAPLICADOS (08/09)", width: "130px" },
                                    { label: "9. (=) SALDO\nACUMULADO", width: "130px" }
                                ].map((col, i) => (
                                    <th key={i} style={{
                                        padding: "12px 16px",
                                        textAlign: i <= 2 ? "left" : "right",
                                        fontSize: "10px",
                                        fontFamily: "Montserrat",
                                        fontWeight: 700,
                                        color: "#64748b",
                                        letterSpacing: "0.06em",
                                        textTransform: "uppercase",
                                        whiteSpace: "pre-line",
                                        lineHeight: 1.4,
                                        borderBottom: "2px solid #e2e8f0",
                                        width: col.width,
                                        cursor: i > 2 ? "pointer" : "default"
                                    }}>
                                        {col.label}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={9} style={{ padding: "40px", textAlign: "center", color: "#94a3b8", fontFamily: "Montserrat", fontSize: "12px" }}>
                                        Cargando registros...
                                    </td>
                                </tr>
                            ) : registros.length === 0 ? (
                                <tr>
                                    <td colSpan={9} style={{ padding: "40px", textAlign: "center", color: "#94a3b8", fontFamily: "Montserrat", fontSize: "12px" }}>
                                        No se encontraron registros.
                                    </td>
                                </tr>
                            ) : registros.map((doc, i) => (
                                <tr key={doc.uuid}
                                    style={{
                                        borderBottom: "1px solid #f8fafc",
                                        transition: "background 0.15s"
                                    }}
                                    onMouseEnter={e =>
                                        e.currentTarget.style.background = "#fafbff"}
                                    onMouseLeave={e =>
                                        e.currentTarget.style.background = "white"}
                                >
                                    <td style={{ padding: "14px 16px" }}>
                                        <div style={{
                                            display: "flex",
                                            alignItems: "center", gap: "8px"
                                        }}>
                                            <div style={{
                                                width: "7px", height: "7px",
                                                borderRadius: "50%", flexShrink: 0,
                                                background:
                                                    doc.segmento === "PUE" ? "#6B84F3" :
                                                        doc.segmento === "PPD" ? "#785799" :
                                                            "#CBD0DA"
                                            }} />
                                            <span style={{
                                                fontFamily: "JetBrains Mono, monospace",
                                                fontSize: "12px",
                                                color: "#1e293b"
                                            }}>
                                                {doc.uuid}
                                            </span>
                                        </div>
                                    </td>

                                    <td style={{ padding: "14px 16px" }}>
                                        <span style={{
                                            padding: "3px 10px",
                                            borderRadius: "6px",
                                            fontSize: "11px",
                                            fontFamily: "Montserrat",
                                            fontWeight: 700,
                                            background:
                                                doc.segmento === "PUE"
                                                    ? "#6B84F315" :
                                                    doc.segmento === "PPD"
                                                        ? "#78579915" :
                                                        "#CBD0DA30",
                                            color:
                                                doc.segmento === "PUE" ? "#6B84F3" :
                                                    doc.segmento === "PPD" ? "#785799" :
                                                        "#94a3b8"
                                        }}>
                                            {doc.segmento}
                                        </span>
                                    </td>

                                    <td style={{ padding: "14px 16px" }}>
                                        <span style={{
                                            fontSize: "11px",
                                            fontFamily: "Montserrat",
                                            fontWeight: 700,
                                            color: doc.flujo === "EMITIDOS"
                                                ? "#6B84F3" : "#FF8A65",
                                            letterSpacing: "0.04em"
                                        }}>
                                            {doc.flujo}
                                        </span>
                                    </td>

                                    {[
                                        doc.conceptos?.["1. (+) Total Facturado"] ?? 0,
                                        doc.conceptos?.["2. (-) Notas de Crédito (01)"] ?? 0,
                                        doc.conceptos?.["4. (-) Devoluciones (03)"] ?? 0,
                                        doc.conceptos?.["7. (-) Anticipo (07)"] ?? 0,
                                        doc.conceptos?.["8. (-) Pagos Aplicados (08/09)"] ?? 0,
                                    ].map((val, j) => (
                                        <td key={j} style={{
                                            padding: "14px 16px",
                                            textAlign: "right",
                                            fontFamily: "JetBrains Mono, monospace",
                                            fontSize: "13px",
                                            color: val === 0 ? "#cbd5e1" :
                                                j === 0 ? "#26A69A" :
                                                    j === 4 ? "#FF8A65" :
                                                        "#ef4444",
                                            fontWeight: val === 0 ? 400 : 600
                                        }}>
                                            {val === 0
                                                ? "0.00"
                                                : formatMoney(val)}
                                        </td>
                                    ))}

                                    <td style={{
                                        padding: "14px 16px",
                                        textAlign: "right",
                                        fontFamily: "JetBrains Mono, monospace",
                                        fontSize: "13px",
                                        fontWeight: 700,
                                        color: doc.saldo_acumulado > 0 ? "#26A69A" :
                                            doc.saldo_acumulado < 0 ? "#ef4444" :
                                                "#cbd5e1"
                                    }}>
                                        {formatMoney(doc.saldo_acumulado)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div style={{
                    display: "flex", justifyContent: "space-between",
                    alignItems: "center",
                    padding: "16px 24px"
                }}>
                    <span style={{
                        fontSize: "12px", color: "#94a3b8",
                        fontFamily: "Montserrat"
                    }}>
                        Página {filtros.page} de {Math.max(1, Math.ceil(total / filtros.limit))}
                    </span>
                    <div style={{ display: "flex", gap: "8px" }}>
                        <button
                            onClick={() => setFiltros(p =>
                                ({ ...p, page: Math.max(1, p.page - 1) }))}
                            disabled={filtros.page === 1}
                            style={{
                                padding: "6px 14px", borderRadius: "8px",
                                border: "1px solid #e2e8f0",
                                fontFamily: "Montserrat", fontSize: "12px",
                                fontWeight: 600,
                                background: filtros.page === 1 ? "#f8fafc" : "white",
                                color: filtros.page === 1 ? "#cbd5e1" : "#1e293b",
                                cursor: filtros.page === 1 ? "not-allowed" : "pointer"
                            }}
                        >
                            ← Anterior
                        </button>
                        <button
                            onClick={() => setFiltros(p =>
                                ({ ...p, page: p.page + 1 }))}
                            disabled={filtros.page >= Math.ceil(total / filtros.limit)}
                            style={{
                                padding: "6px 14px", borderRadius: "8px",
                                border: filtros.page >= Math.ceil(total / filtros.limit) ? "1px solid #e2e8f0" : "none",
                                fontFamily: "Montserrat", fontSize: "12px",
                                fontWeight: 600,
                                background: filtros.page >= Math.ceil(total / filtros.limit) ? "#f8fafc" : "#6B84F3",
                                color: filtros.page >= Math.ceil(total / filtros.limit) ? "#cbd5e1" : "white",
                                cursor: filtros.page >= Math.ceil(total / filtros.limit) ? "not-allowed" : "pointer"
                            }}
                        >
                            Siguiente →
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetalleUUIDView;
