/* eslint-disable react/prop-types */
/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import {
    Download, Search, Layers, DollarSign, Calendar, Clock,
    GitBranch, FileText, CreditCard, X, Activity, FileCheck, FileMinus, File
} from 'lucide-react';
import {
    ComposedChart, Area, Scatter, XAxis, YAxis,
    CartesianGrid, Tooltip, ReferenceLine,
    ResponsiveContainer
} from 'recharts';
import useFilterStore from '../../stores/useFilterStore';
import { useTrazabilidadStore } from '../../stores/useTrazabilidadStore';
import dashboardService from './dashboardService';

const formatMoney = (amount, includeSign = false) => {
    if (amount === undefined || amount === null) return "$0.00";
    const str = new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD', minimumFractionDigits: 2
    }).format(Math.abs(amount));
    if (includeSign) { return amount < 0 ? `-${str}` : str; }
    return str;
};

// Iconos por tipo de concepto
const iconoConcepto = (concepto) => {
    if (!concepto) return { icon: File, color: "#CBD0DA", bg: "#CBD0DA15" };
    if (concepto.includes("Total Facturado") || concepto.startsWith("1."))
        return { icon: FileCheck, color: "#26A69A", bg: "#26A69A15" }
    if (concepto.includes("Notas de Crédito") || concepto.startsWith("2."))
        return { icon: FileMinus, color: "#FF8A65", bg: "#FF8A6515" }
    if (concepto.includes("Anticipo") || concepto.startsWith("3."))
        return { icon: FileMinus, color: "#FF8A65", bg: "#FF8A6515" }
    if (concepto.includes("Devoluciones") || concepto.startsWith("4."))
        return { icon: FileMinus, color: "#FF8A65", bg: "#FF8A6515" }
    if (concepto.includes("Pagos Aplicados") || concepto.startsWith("8.") || concepto.includes("PAGO"))
        return { icon: FileMinus, color: "#6B84F3", bg: "#6B84F315" }
    // Fallback
    return { icon: File, color: "#CBD0DA", bg: "#CBD0DA15" }
}

// Chip de tipo relación
const chipRelacion = (tipo) => {
    const estilos = {
        "ORIGINAL": { bg: "#26A69A15", color: "#26A69A", border: "#26A69A30" },
        "01": { bg: "#FF8A6515", color: "#FF8A65", border: "#FF8A6530" },
        "02": { bg: "#6B84F315", color: "#6B84F3", border: "#6B84F330" },
        "03": { bg: "#FFCA2815", color: "#b8860b", border: "#FFCA2830" },
        "04": { bg: "#CBD0DA20", color: "#64748b", border: "#CBD0DA40" },
        "07": { bg: "#78579915", color: "#785799", border: "#78579930" },
        "08": { bg: "#78579915", color: "#785799", border: "#78579930" },
        "PAGO": { bg: "#6B84F315", color: "#6B84F3", border: "#6B84F330" }, // Added to handle current string formats
    }
    const s = estilos[tipo] || estilos["04"]
    return (
        <span style={{
            padding: "4px 10px",
            borderRadius: "20px",
            fontSize: "10px",
            fontFamily: "Montserrat",
            fontWeight: 700,
            background: s.bg,
            color: s.color,
            border: `1px solid ${s.border}`,
            letterSpacing: "0.04em"
        }}>
            {tipo}
        </span>
    )
}

const EvolucionSaldoChart = ({ data }) => {
    const [tooltipVisible, setTooltipVisible] = useState(true);

    const CustomDot = (props) => {
        const { cx, cy, payload } = props
        const color = payload.concepto?.startsWith("1.") ? "#26A69A" :
            payload.concepto?.startsWith("8.") ? "#FF8A65" :
                "#6B84F3"
        return (
            <g onClick={() => setTooltipVisible(true)} style={{ cursor: "pointer" }}>
                <circle cx={cx} cy={cy} r={6} fill="white" stroke={color} strokeWidth={2.5} />
                <circle cx={cx} cy={cy} r={3} fill={color} />
            </g>
        )
    }

    const CustomTooltip = ({ active, payload, onClose }) => {
        if (!active || !payload?.length) return null
        const d = payload[0]?.payload
        if (!d) return null

        return (
            <div style={{
                background: "white",
                borderRadius: "20px",
                padding: "24px 28px",
                minWidth: "340px",
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

                {/* Fecha y Badge */}
                <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "16px",
                    paddingRight: "24px"
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <Calendar size={14} color="#94a3b8" />
                        <p style={{
                            fontFamily: "JetBrains Mono",
                            fontSize: "12px",
                            color: "#64748b",
                            fontWeight: 600
                        }}>
                            {d.fecha ? d.fecha.slice(0, 10) : ''}
                        </p>
                    </div>
                    <span style={{
                        padding: "4px 12px",
                        borderRadius: "20px",
                        fontSize: "10px",
                        fontFamily: "Montserrat",
                        fontWeight: 800,
                        letterSpacing: "0.04em",
                        background: d.monto >= 0 ? "#26A69A15" : "#FF8A6515",
                        color: d.monto >= 0 ? "#26A69A" : "#FF8A65"
                    }}>
                        {d.monto >= 0 ? "INGRESO" : "EGRESO"}
                    </span>
                </div>

                {/* Concepto / Evento */}
                <div style={{
                    display: "flex",
                    gap: "10px",
                    marginBottom: "20px",
                    background: "#f8fafc",
                    padding: "12px",
                    borderRadius: "12px",
                    border: "1px solid #f1f5f9"
                }}>
                    <div style={{
                        width: "32px",
                        height: "32px",
                        borderRadius: "10px",
                        background: "white",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        boxShadow: "0 2px 4px rgba(0,0,0,0.04)"
                    }}>
                        <Activity size={16} color="#6B84F3" />
                    </div>
                    <div style={{ flex: 1 }}>
                        <p style={{
                            fontSize: "10px",
                            color: "#94a3b8",
                            fontFamily: "Montserrat",
                            fontWeight: 700,
                            textTransform: "uppercase",
                            letterSpacing: "0.05em"
                        }}>
                            Evento
                        </p>
                        <p style={{
                            fontFamily: "Montserrat",
                            fontSize: "13px",
                            fontWeight: 600,
                            color: "#1e293b",
                            lineHeight: 1.3
                        }}>
                            {d.concepto}
                        </p>
                    </div>
                </div>

                {/* Valores en Grid */}
                <div style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "20px"
                }}>
                    <div>
                        <p style={{
                            fontSize: "10px",
                            color: "#94a3b8",
                            fontFamily: "Montserrat",
                            fontWeight: 700,
                            textTransform: "uppercase",
                            letterSpacing: "0.08em",
                            marginBottom: "8px"
                        }}>
                            Monto
                        </p>
                        <p style={{
                            fontFamily: "JetBrains Mono",
                            fontSize: "26px",
                            fontWeight: 700,
                            color: d.monto >= 0 ? "#26A69A" : "#FF8A65",
                            lineHeight: 1
                        }}>
                            {formatMoney(d.monto)}
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
                            marginBottom: "8px"
                        }}>
                            Saldo Acum.
                        </p>
                        <p style={{
                            fontFamily: "JetBrains Mono",
                            fontSize: "26px",
                            fontWeight: 700,
                            color: d.saldo >= 0 ? "#6B84F3" : "#ef4444",
                            lineHeight: 1
                        }}>
                            {formatMoney(d.saldo)}
                        </p>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={data} margin={{ top: 10, right: 20, left: 80, bottom: 30 }}>
                <defs>
                    <linearGradient id="gradSaldo" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6B84F3" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#6B84F3" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                    dataKey="fecha"
                    tickFormatter={v => (v && typeof v === 'string') ? v.slice(0, 10) : v}
                    tick={{ fontSize: 10, fontFamily: "Montserrat", fill: "#94a3b8", dy: 10 }}
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis
                    tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
                    tick={{ fontSize: 10, fontFamily: "JetBrains Mono", fill: "#94a3b8" }}
                    axisLine={false}
                    tickLine={false}
                />
                <ReferenceLine
                    y={0}
                    stroke="#26A69A"
                    strokeWidth={1.5}
                    strokeDasharray="6 3"
                    label={{
                        value: "Liquidación",
                        position: "top",
                        offset: 10,
                        fontSize: 10,
                        fontFamily: "Montserrat",
                        fill: "#26A69A",
                        fontWeight: 700
                    }}
                />
                <Tooltip
                    content={<CustomTooltip onClose={() => setTooltipVisible(false)} />}
                    active={tooltipVisible ? undefined : false}
                    trigger="click"
                />
                <Area type="monotone" dataKey="saldo" stroke="#6B84F3" strokeWidth={2} fill="url(#gradSaldo)" dot={<CustomDot />} activeDot={{ r: 8, fill: "#6B84F3", stroke: "white", strokeWidth: 2 }} />
            </ComposedChart>
        </ResponsiveContainer>
    )
}

const KPICard = ({ title, value, icon: Icon, accentColor }) => (
    <div style={{
        background: "white", borderRadius: "16px", padding: "16px",
        display: "flex", alignItems: "center", gap: "16px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
        borderBottom: `3px solid ${accentColor}`
    }}>
        <div style={{
            width: "42px", height: "42px", borderRadius: "12px",
            background: `${accentColor}15`, display: "flex",
            alignItems: "center", justifyContent: "center"
        }}>
            <Icon size={20} color={accentColor} />
        </div>
        <div>
            <p style={{ fontSize: "11px", color: "#64748b", fontFamily: "Montserrat", fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: "4px" }}>
                {title}
            </p>
            <p style={{ fontSize: "16px", fontWeight: 800, color: "#1e293b", fontFamily: "JetBrains Mono" }}>
                {value}
            </p>
        </div>
    </div>
)


const TraceabilityView = () => {
    const { periodo } = useFilterStore();
    const { uuidSeleccionado: globalUUID, setUUIDTrazabilidad } = useTrazabilidadStore();

    const [uuidsDisponibles, setUuidsDisponibles] = useState([]);
    const [busqueda, setBusqueda] = useState('');
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);

    const [uuidSeleccionado, setUuidSeleccionado] = useState(globalUUID);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [filtroEstado, setFiltroEstado] = useState("TODOS");
    const [filtroEventos, setFiltroEventos] = useState("TODOS");

    // Sincronizar store local
    useEffect(() => {
        if (globalUUID && globalUUID !== uuidSeleccionado) {
            setUuidSeleccionado(globalUUID);
        }
    }, [globalUUID]);

    // Recargar la lista desde cero cuando cambia el periodo
    useEffect(() => {
        setFiltroEstado("TODOS");
        setFiltroEventos("TODOS");
        setUuidsDisponibles([]);
        setPage(1);
        setHasMore(true);
        loadUuidsDisponibles(1, true);
    }, [periodo]);

    // Cargar detalles cuando se selecciona un UUID específico
    useEffect(() => {
        if (uuidSeleccionado) {
            loadDetalleUuid(uuidSeleccionado);
        } else {
            setData(null);
        }
    }, [uuidSeleccionado]);

    const loadUuidsDisponibles = async (targetPage, isFirstLoad = false) => {
        try {
            if (isFirstLoad) setLoading(true);
            else setLoadingMore(true);

            const limit = 50;
            const res = await dashboardService.getUuidsDisponibles(periodo, targetPage, limit);
            console.log(`DEBUG LOAD UUIDS (Page ${targetPage}):`, res);

            if (Array.isArray(res)) {
                if (res.length < limit) setHasMore(false);

                if (isFirstLoad) {
                    setUuidsDisponibles(res);
                } else {
                    setUuidsDisponibles(prev => [...prev, ...res]);
                }
                setPage(targetPage);
            } else {
                setError(`Unexpected response format: ${JSON.stringify(res)}`);
            }
        } catch (error) {
            console.error("Error loading UUIDs list:", error);
            setError(`Error fetching UUIDs: ${error.message}`);
        } finally {
            if (isFirstLoad) setLoading(false);
            else setLoadingMore(false);
        }
    };

    const loadDetalleUuid = async (uuid) => {
        try {
            setLoading(true);
            setError(null);
            const res = await dashboardService.getTrazabilidad(uuid);
            console.log("DEBUG LOAD DETALLE:", res);
            setData(res);
        } catch (error) {
            console.error("Error loading UUID detail:", error);
            setError(`Error fetching detail for ${uuid}: ${error.message} ${error.response?.data?.detail || ''}`);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectUUID = (uuid) => {
        setUuidSeleccionado(uuid);
        setUUIDTrazabilidad(uuid); // Keep store in sync
    };

    const handleExportCSV = () => {
        if (!data || !data.eventos) return;
        const csvRows = [
            ['#', 'FECHA/HORA', 'CONCEPTO', 'TIPO RELACIÓN', 'UUID RELACIONADO', 'MONTO', 'SALDO ACUMULADO']
        ];
        data.eventos.forEach((e, i) => {
            csvRows.push([
                i + 1, e.fecha, `"${e.concepto}"`, e.tipo_relacion,
                e.uuid_relacionado || '', e.monto, e.saldo_acumulado
            ]);
        });
        const csvContent = "data:text/csv;charset=utf-8," + csvRows.map(r => r.join(',')).join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `Trazabilidad_${uuidSeleccionado || 'General'}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const uuidsFiltrados = uuidsDisponibles.filter(u => {
        const matchBusqueda = (u.uuid || "").toLowerCase().includes((busqueda || "").toLowerCase());
        const matchEstado = filtroEstado === "TODOS" || u.estado === filtroEstado;
        const matchEventos = filtroEventos === "TODOS"
            || (filtroEventos === "MULTIPLES" && u.total_eventos > 1)
            || (filtroEventos === "SIMPLE" && u.total_eventos === 1);
        return matchBusqueda && matchEstado && matchEventos;
    });

    return (
        <div style={{ padding: "24px", background: "#f8fafc", minHeight: "100vh" }}>
            {/* HEADER DE LA VISTA */}
            <div style={{
                display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "20px 24px",
                background: "white", borderRadius: "16px", borderLeft: "4px solid #785799",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)", marginBottom: "24px"
            }}>
                <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                        <h2 style={{ fontSize: "20px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.05em", textTransform: "uppercase" }}>
                            Trazabilidad de UUID Fiscal
                        </h2>
                    </div>
                    <p style={{ fontSize: "13px", fontFamily: "Montserrat", color: "#94a3b8", fontWeight: 400 }}>
                        Seguimiento cronológico de eventos y pagos por folio CFDI
                    </p>
                </div>
                <button onClick={handleExportCSV} style={{ display: "flex", alignItems: "center", gap: "8px", background: "#785799", color: "white", border: "none", borderRadius: "10px", padding: "9px 18px", cursor: "pointer", fontFamily: "Montserrat", fontSize: "13px", fontWeight: 700 }}>
                    <Download size={15} /> EXPORTAR TRAZA
                </button>
            </div>

            {/* LAYOUT PRINCIPAL CON GRID */}
            <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "16px", marginBottom: "16px" }}>

                {/* PANEL SELECTOR DE UUID */}
                <div style={{ background: "white", borderRadius: "16px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", display: "flex", flexDirection: "column", height: "calc(100vh - 180px)", minHeight: "500px" }}>
                    <div style={{ padding: "16px 16px 12px" }}>
                        <p style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "10px" }}>Seleccionar UUID</p>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "10px", padding: "8px 12px", marginBottom: "12px" }}>
                            <Search size={14} color="#94a3b8" />
                            <input
                                placeholder="Buscar UUID..."
                                value={busqueda}
                                onChange={e => setBusqueda(e.target.value)}
                                style={{
                                    border: "none", background: "transparent",
                                    fontFamily: "Montserrat", fontSize: "12px",
                                    color: "#1e293b", outline: "none",
                                    flex: 1, minWidth: 0
                                }}
                            />
                            {busqueda && (
                                <button
                                    onClick={() => setBusqueda('')}
                                    style={{ background: "none", border: "none", cursor: "pointer", color: "#94a3b8", display: "flex", alignItems: "center", padding: "2px" }}
                                >
                                    <X size={12} />
                                </button>
                            )}
                        </div>

                        {/* FILTRO 1 — Por Estado */}
                        <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "6px" }}>Estado</p>
                        <div style={{ display: "flex", gap: "6px", marginBottom: "12px", flexWrap: "wrap" }}>
                            {[
                                { value: "TODOS", label: "Todos", color: "#64748b", bg: "#f1f5f9" },
                                { value: "LIQUIDADO", label: "✓ Liquidado", color: "#26A69A", bg: "#26A69A15" },
                                { value: "INSOLUTO", label: "● Insoluto", color: "#FF8A65", bg: "#FF8A6515" },
                                { value: "SALDO_NEGATIVO", label: "✕ Negativo", color: "#ef4444", bg: "#ef444415" },
                            ].map(op => (
                                <button
                                    key={op.value}
                                    onClick={() => setFiltroEstado(op.value)}
                                    style={{
                                        padding: "4px 10px", borderRadius: "20px", border: "none", cursor: "pointer",
                                        fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, letterSpacing: "0.04em", transition: "all 0.15s",
                                        background: filtroEstado === op.value ? op.bg : "#f8fafc",
                                        color: filtroEstado === op.value ? op.color : "#94a3b8",
                                        outline: filtroEstado === op.value ? `1px solid ${op.color}40` : "none"
                                    }}
                                >
                                    {op.label}
                                </button>
                            ))}
                        </div>

                        {/* FILTRO 2 — Por Número de Eventos */}
                        <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "6px" }}>Eventos</p>
                        <div style={{ display: "flex", gap: "6px", marginBottom: "8px" }}>
                            {[
                                { value: "TODOS", label: "Todos" },
                                { value: "MULTIPLES", label: "2+ eventos" },
                                { value: "SIMPLE", label: "1 evento" },
                            ].map(op => (
                                <button
                                    key={op.value}
                                    onClick={() => setFiltroEventos(op.value)}
                                    style={{
                                        flex: 1, padding: "5px 8px", borderRadius: "8px", border: "none", cursor: "pointer",
                                        fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, transition: "all 0.15s",
                                        background: filtroEventos === op.value ? "#785799" : "#f8fafc",
                                        color: filtroEventos === op.value ? "white" : "#94a3b8"
                                    }}
                                >
                                    {op.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Contador resultado */}
                    <div style={{ padding: "0 16px 10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "10px", color: "#94a3b8", fontFamily: "Montserrat" }}>
                            {uuidsFiltrados.length} UUIDs {uuidsFiltrados.length > 100 && "(Top 100)"}
                        </span>
                        {(filtroEstado !== "TODOS" || filtroEventos !== "TODOS" || busqueda !== "") && (
                            <button
                                onClick={() => { setFiltroEstado("TODOS"); setFiltroEventos("TODOS"); setBusqueda(""); }}
                                style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 600, color: "#6B84F3", background: "none", border: "none", cursor: "pointer", padding: 0 }}
                            >
                                × Limpiar
                            </button>
                        )}
                    </div>

                    {/* Lista de UUIDs con Scroll Infinito */}
                    <div
                        style={{ overflowY: "auto", flex: 1, borderTop: "1px solid #f1f5f9", paddingBottom: "12px" }}
                        onScroll={e => {
                            const el = e.currentTarget;
                            if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50 && hasMore && !loadingMore) {
                                loadUuidsDisponibles(page + 1);
                            }
                        }}
                    >
                        {uuidsFiltrados.length === 0 && !loading ? (
                            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "200px", gap: "8px" }}>
                                <p style={{ fontFamily: "Montserrat", fontSize: "12px", color: "#94a3b8", textAlign: "center" }}>Sin resultados para<br />los filtros aplicados</p>
                                <button onClick={() => { setFiltroEstado("TODOS"); setFiltroEventos("TODOS"); setBusqueda(""); }} style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 600, color: "#6B84F3", background: "none", border: "none", cursor: "pointer" }}>Limpiar filtros</button>
                            </div>
                        ) : (
                            <>
                                {uuidsFiltrados.map(u => (
                                    <div key={u.uuid} onClick={() => handleSelectUUID(u.uuid)} style={{ padding: "12px 16px", cursor: "pointer", background: uuidSeleccionado === u.uuid ? "#6B84F308" : "transparent", borderLeft: uuidSeleccionado === u.uuid ? "3px solid #785799" : "3px solid transparent", borderBottom: "1px solid #f8fafc", transition: "all 0.15s" }}>
                                        <p style={{ fontFamily: "JetBrains Mono", fontSize: "11px", color: uuidSeleccionado === u.uuid ? "#785799" : "#475569", fontWeight: uuidSeleccionado === u.uuid ? 700 : 400, marginBottom: "6px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                            {u.uuid}
                                        </p>
                                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                            <span style={{ padding: "2px 8px", borderRadius: "20px", fontSize: "9px", fontFamily: "Montserrat", fontWeight: 800, letterSpacing: "0.06em", background: u.estado === "LIQUIDADO" ? "#26A69A15" : u.estado === "INSOLUTO" ? "#FF8A6515" : "#ef444415", color: u.estado === "LIQUIDADO" ? "#26A69A" : u.estado === "INSOLUTO" ? "#FF8A65" : "#ef4444" }}>
                                                {u.estado === "LIQUIDADO" ? "✓ LIQUIDADO" : u.estado === "INSOLUTO" ? "● INSOLUTO" : "✕ NEG"}
                                            </span>
                                            <span style={{ fontFamily: "JetBrains Mono", fontSize: "11px", fontWeight: 700, color: u.ultimo_saldo === 0 ? "#26A69A" : u.ultimo_saldo > 0 ? "#FF8A65" : "#ef4444" }}>
                                                {formatMoney(u.ultimo_saldo, true)}
                                            </span>
                                        </div>
                                        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px" }}>
                                            <span style={{ fontSize: "9px", color: "#94a3b8", fontFamily: "Montserrat" }}>{u.total_eventos} eventos</span>
                                            <span style={{ fontSize: "9px", color: "#94a3b8", fontFamily: "JetBrains Mono" }}>{(u.ultimo_evento || "").split('T')[0] || u.ultimo_evento}</span>
                                        </div>
                                    </div>
                                ))}
                                {loadingMore && (
                                    <div style={{ padding: "16px", textAlign: "center", color: "#94a3b8", fontSize: "11px", fontFamily: "Montserrat", fontWeight: 600 }}>
                                        Cargando más folios...
                                    </div>
                                )}
                                {!hasMore && uuidsFiltrados.length > 0 && (
                                    <div style={{ padding: "16px", textAlign: "center", color: "#cbd5e1", fontSize: "11px", fontFamily: "Montserrat" }}>
                                        No hay más folios para este periodo.
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>

                {/* COLUMNA DERECHA ALINEADA CON LA IZQUIERDA */}
                <div style={{ height: "calc(100vh - 180px)", minHeight: "500px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "16px", paddingRight: "4px" }}>
                    {!uuidSeleccionado || !data ? (
                        /* ESTADO INICIAL */
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: "16px", background: "white", borderRadius: "16px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                            <div style={{ width: "64px", height: "64px", borderRadius: "20px", background: "#78579915", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                <GitBranch size={32} color="#785799" />
                            </div>
                            <p style={{ fontFamily: "Montserrat", fontSize: "16px", fontWeight: 700, color: "#1e293b" }}>Selecciona un UUID</p>
                            <p style={{ fontFamily: "Montserrat", fontSize: "13px", color: "#94a3b8", textAlign: "center", maxWidth: "300px" }}>Elige un folio fiscal del panel izquierdo para ver su trazabilidad completa de eventos</p>
                            {error && (
                                <div style={{
                                    marginTop: "20px", padding: "16px",
                                    background: "#fff1f2", color: "#e11d48",
                                    borderRadius: "12px", border: "1px solid #fda4af",
                                    fontFamily: "Montserrat", fontSize: "12px",
                                    maxWidth: "80%", textAlign: "center"
                                }}>
                                    <strong>Aviso:</strong> {error.includes("404") ?
                                        "Este folio fiscal no cuenta con registros de trazabilidad en el sistema. Seleccione otro UUID de la lista." :
                                        error}
                                </div>
                            )}
                        </div>
                    ) : (
                        <>
                            {/* KPI CARDS */}
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "16px" }}>
                                <KPICard title="Total Eventos" value={data.kpis.total_eventos.toLocaleString()} icon={Layers} accentColor="#6B84F3" />
                                <KPICard title="Saldo Final" value={formatMoney(data.kpis.saldo_final, true)} icon={DollarSign} accentColor={data.kpis.estado === "LIQUIDADO" ? "#26A69A" : data.kpis.estado === "INSOLUTO" ? "#FF8A65" : "#ef4444"} />
                                <KPICard title="Primer Evento" value={data.kpis.primer_evento.split('T')[0] || data.kpis.primer_evento} icon={Calendar} accentColor="#FFCA28" />
                                <KPICard title="Último Evento" value={data.kpis.ultimo_evento.split('T')[0] || data.kpis.ultimo_evento} icon={Clock} accentColor="#785799" />
                            </div>

                            {/* BARRA DE PROGRESO DE LIQUIDACIÓN */}
                            {data.kpis.monto_original > 0 && (
                                <div style={{ background: "white", borderRadius: "16px", padding: "16px 20px", marginBottom: "16px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                                        <span style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, color: "#64748b", letterSpacing: "0.06em", textTransform: "uppercase" }}>Progreso de Liquidación</span>
                                        <span style={{ fontSize: "13px", fontFamily: "JetBrains Mono", fontWeight: 700, color: data.kpis.pct_liquidado >= 100 ? "#26A69A" : data.kpis.pct_liquidado >= 50 ? "#FFCA28" : "#FF8A65" }}>{Math.min(data.kpis.pct_liquidado, 100).toFixed(1)}% liquidado</span>
                                    </div>
                                    <div style={{ background: "#f1f5f9", borderRadius: "20px", height: "10px", overflow: "hidden" }}>
                                        <div style={{ height: "100%", width: `${Math.min(data.kpis.pct_liquidado, 100)}%`, borderRadius: "20px", background: data.kpis.pct_liquidado >= 100 ? "linear-gradient(90deg, #26A69A, #00BCD4)" : data.kpis.pct_liquidado >= 50 ? "linear-gradient(90deg, #FFCA28, #FF8A65)" : "linear-gradient(90deg, #FF8A65, #ef4444)", transition: "width 0.6s ease" }} />
                                    </div>
                                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: "8px" }}>
                                        <span style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "JetBrains Mono" }}>Original: {formatMoney(data.kpis.monto_original)}</span>
                                        <span style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "JetBrains Mono" }}>Pagado: {formatMoney(data.kpis.total_pagado)}</span>
                                        <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: data.kpis.saldo_final > 0 ? "#FF8A65" : "#26A69A", fontWeight: 700 }}>Saldo: {formatMoney(data.kpis.saldo_final)}</span>
                                    </div>
                                </div>
                            )}

                            {/* GRÁFICA EVOLUCIÓN DEL SALDO */}
                            <div style={{ background: "white", borderRadius: "16px", padding: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: `4px solid #6B84F3`, flex: 1, minHeight: "450px" }}>
                                <h3 style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 700, color: "#1e293b", letterSpacing: "0.05em", marginBottom: "16px" }}>EVOLUCIÓN DEL SALDO ACUMULADO</h3>
                                <EvolucionSaldoChart key={uuidSeleccionado} data={data.evolucion_saldo} />
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* TABLA HISTORIAL DE EVENTOS — ANCHO COMPLETO ABAJO */}
            {
                uuidSeleccionado && data && (
                    <div style={{ background: "white", borderRadius: "20px", overflow: "hidden", boxShadow: `0 0 0 1px rgba(0,0,0,0.04), 0 4px 24px rgba(0,0,0,0.06)` }}>
                        {/* Header de la tabla */}
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 24px", borderBottom: "2px solid #f1f5f9" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#6B84F315", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                    <GitBranch size={16} color="#6B84F3" />
                                </div>
                                <div>
                                    <p style={{ fontSize: "15px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", lineHeight: 1.2 }}>Historial de Eventos</p>
                                    <p style={{ fontSize: "11px", fontFamily: "Montserrat", color: "#94a3b8", fontWeight: 500, marginTop: "2px" }}>UUID raíz: <span style={{ fontFamily: "JetBrains Mono", color: "#6B84F3", fontSize: "11px" }}>{uuidSeleccionado}</span></p>
                                </div>
                            </div>
                        </div>

                        {/* Tabla */}
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ background: "#f8fafc" }}>
                                    {[
                                        { label: "#", w: "48px", align: "center" },
                                        { label: "FOLIO FISCAL", w: "240px", align: "left" },
                                        { label: "FECHA", w: "120px", align: "left" },
                                        { label: "CONCEPTO", w: "200px", align: "left" },
                                        { label: "TIPO\nRELACIÓN", w: "100px", align: "center" },
                                        { label: "UUID RELACIONADO", w: "auto", align: "left" },
                                        { label: "MONTO", w: "130px", align: "right" },
                                        { label: "SALDO\nACUMULADO", w: "130px", align: "right" }
                                    ].map((col, i) => (
                                        <th key={i} style={{ padding: "12px 16px", textAlign: col.align, fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#64748b", letterSpacing: "0.08em", textTransform: "uppercase", whiteSpace: "pre-line", lineHeight: 1.4, borderBottom: "2px solid #e2e8f0", width: col.w }}>
                                            {col.label}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.eventos.map((ev, i) => {
                                    const { icon: Icon, color, bg } = iconoConcepto(ev.concepto);
                                    const esOriginal = ev.tipo_relacion === "ORIGINAL";
                                    const esUltimo = i === data.eventos.length - 1;

                                    return (
                                        <tr key={i}
                                            style={{
                                                borderBottom: esUltimo ? "none" : "1px solid #f1f5f9",
                                                background: esOriginal ? "#f0fdf9" : "white",
                                                transition: "background 0.15s"
                                            }}
                                            onMouseEnter={e => { if (!esOriginal) e.currentTarget.style.background = "#fafbff" }}
                                            onMouseLeave={e => { e.currentTarget.style.background = esOriginal ? "#f0fdf9" : "white" }}
                                        >
                                            {/* # */}
                                            <td style={{ padding: "16px", textAlign: "center", fontSize: "12px", fontFamily: "Montserrat", fontWeight: 700, color: "#cbd5e1" }}>{i + 1}</td>

                                            {/* Folio Fiscal (Timeline) */}
                                            <td style={{ padding: "16px" }}>
                                                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flexShrink: 0 }}>
                                                        <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: color, border: `2px solid white`, boxShadow: `0 0 0 2px ${color}40`, flexShrink: 0 }} />
                                                        {!esUltimo && (
                                                            <div style={{ width: "2px", height: "36px", background: `linear-gradient(${color}60, transparent)`, marginTop: "2px" }} />
                                                        )}
                                                    </div>
                                                    <span style={{ fontFamily: "JetBrains Mono", fontSize: "12px", color: "#1e293b", letterSpacing: "-0.01em" }}>
                                                        {ev.folio_fiscal || uuidSeleccionado}
                                                    </span>
                                                </div>
                                            </td>

                                            {/* Fecha */}
                                            <td style={{ padding: "16px" }}>
                                                <span style={{ fontFamily: "JetBrains Mono", fontSize: "12px", color: "#64748b", background: "#f8fafc", padding: "3px 8px", borderRadius: "6px" }}>
                                                    {ev.fecha ? ev.fecha.slice(0, 10) : ''}
                                                </span>
                                            </td>

                                            {/* Concepto */}
                                            <td style={{ padding: "16px" }}>
                                                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                                    <div style={{ width: "28px", height: "28px", borderRadius: "8px", background: bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                                                        <Icon size={14} color={color} />
                                                    </div>
                                                    <span style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 600, color: "#334155", lineHeight: 1.3 }}>{ev.concepto}</span>
                                                </div>
                                            </td>

                                            {/* Tipo Relación */}
                                            <td style={{ padding: "16px", textAlign: "center" }}>
                                                {chipRelacion(ev.tipo_relacion)}
                                            </td>

                                            {/* UUID Relacionado */}
                                            <td style={{ padding: "16px" }}>
                                                {ev.uuid_relacionado ? (
                                                    <span
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            handleSelectUUID(ev.uuid_relacionado);
                                                        }}
                                                        title="Ver trazabilidad"
                                                        style={{ fontFamily: "JetBrains Mono", fontSize: "12px", color: "#6B84F3", cursor: "pointer", textDecoration: "none", borderBottom: "1px dashed #6B84F360", paddingBottom: "1px", transition: "color 0.15s" }}
                                                    >
                                                        {ev.uuid_relacionado}
                                                    </span>
                                                ) : (
                                                    <span style={{ color: "#cbd5e1", fontSize: "14px" }}>—</span>
                                                )}
                                            </td>

                                            {/* Monto */}
                                            <td style={{ padding: "16px", textAlign: "right" }}>
                                                <span style={{ fontFamily: "JetBrains Mono", fontSize: "13px", fontWeight: 700, color: esOriginal ? "#26A69A" : "#FF8A65" }}>
                                                    {esOriginal ? "+" : "-"}
                                                    {formatMoney(Math.abs(ev.monto))}
                                                </span>
                                            </td>

                                            {/* Saldo Acumulado con progreso */}
                                            <td style={{ padding: "16px", textAlign: "right" }}>
                                                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "4px" }}>
                                                    <span style={{ fontFamily: "JetBrains Mono", fontSize: "13px", fontWeight: 800, color: ev.saldo_acumulado > 0 ? "#26A69A" : ev.saldo_acumulado < 0 ? "#FF8A65" : "#cbd5e1" }}>
                                                        {formatMoney(ev.saldo_acumulado)}
                                                    </span>
                                                    {i > 0 && data.eventos[0].monto > 0 && (
                                                        <div style={{ width: "80px", height: "3px", background: "#f1f5f9", borderRadius: "2px", overflow: "hidden" }}>
                                                            <div style={{ height: "100%", width: `${Math.max(0, Math.min(100, (ev.saldo_acumulado / data.eventos[0].monto) * 100))}%`, background: "#26A69A", borderRadius: "2px", transition: "width 0.5s ease" }} />
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                            <tfoot>
                                <tr style={{ background: "linear-gradient(90deg, #6B84F308, white)", borderTop: "2px solid #e2e8f0" }}>
                                    <td colSpan={6} style={{ padding: "14px 16px", fontSize: "12px", fontFamily: "Montserrat", fontWeight: 700, color: "#64748b", textAlign: "right" }}>
                                        SALDO NETO FINAL
                                    </td>
                                    <td style={{ padding: "14px 16px" }} />
                                    <td style={{ padding: "14px 16px", textAlign: "right" }}>
                                        <span style={{ fontFamily: "JetBrains Mono", fontSize: "15px", fontWeight: 800, color: data.eventos[data.eventos.length - 1]?.saldo_acumulado > 0 ? "#26A69A" : "#FF8A65" }}>
                                            {formatMoney(data.eventos[data.eventos.length - 1]?.saldo_acumulado ?? 0)}
                                        </span>
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                )}
        </div>
    );
};

export default TraceabilityView;
