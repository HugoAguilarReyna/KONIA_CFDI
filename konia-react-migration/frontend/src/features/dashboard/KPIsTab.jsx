/* eslint-disable react/prop-types */
/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import useFilterStore from '../../stores/useFilterStore';
import { useTrazabilidadStore } from '../../stores/useTrazabilidadStore';
import {
    Clock, AlertTriangle, FileCheck, TrendingDown,
    HelpCircle, Shield, Calendar
} from 'lucide-react';

const formatMoney = (amount, includeSign = false) => {
    if (amount === undefined || amount === null) return "$0.00";
    const str = new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD', minimumFractionDigits: 2
    }).format(Math.abs(amount));
    if (includeSign) { return amount < 0 ? `-${str}` : str; }
    return str;
};

// --- Subcomponents ---
const BarraPeriodo = ({ periodo }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'white', padding: '12px 24px', borderRadius: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
        <Calendar size={18} color="#64748b" />
        <span style={{ fontFamily: 'Montserrat', fontSize: '13px', fontWeight: 600, color: '#334155', letterSpacing: '0.05em' }}>
            PERÍODO FISCAL:
        </span>
        <span style={{ fontFamily: 'JetBrains Mono', fontSize: '14px', fontWeight: 700, color: '#6B84F3', background: '#6B84F315', padding: '4px 12px', borderRadius: '20px' }}>
            {periodo}
        </span>
    </div>
);

const BloqueCarteraPPD = ({ data }) => {
    const aging = [
        { label: "0-30 días", key: "0-30d", color: "#26A69A" },
        { label: "31-60 días", key: "31-60d", color: "#FFCA28" },
        { label: "61-90 días", key: "61-90d", color: "#FF8A65" },
        { label: "+90 días", key: "+90d", color: "#ef4444" }
    ];

    return (
        <div style={{ background: "white", borderRadius: "20px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #785799" }}>
            {/* Título */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
                <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#78579915", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Clock size={16} color="#785799" />
                </div>
                <div>
                    <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                        Salud de Cartera PPD
                    </p>
                    <p style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat" }}>
                        Antigüedad de saldo pendiente de cobro
                    </p>
                </div>
            </div>

            {/* KPIs rápidos — 3 chips */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "10px", marginBottom: "20px" }}>
                {[
                    { label: "DSO Promedio", value: `${data.dso_promedio_dias}d`, color: "#785799", sub: "días promedio de cobro" },
                    { label: "Sin REP", value: data.sin_rep_count.toLocaleString(), color: "#FF8A65", sub: formatMoney(data.sin_rep_monto, true) },
                    { label: "Recuperación", value: `${data.tasa_recuperacion}%`, color: "#26A69A", sub: "con complemento pago" }
                ].map((chip, i) => (
                    <div key={i} style={{ background: "#f8fafc", borderRadius: "12px", padding: "12px", borderLeft: `3px solid ${chip.color}` }}>
                        <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>
                            {chip.label}
                        </p>
                        <p style={{ fontSize: "20px", fontFamily: "JetBrains Mono", fontWeight: 800, color: chip.color, lineHeight: 1 }}>
                            {chip.value}
                        </p>
                        <p style={{ fontSize: "10px", fontFamily: "Montserrat", color: "#94a3b8", marginTop: "4px" }}>
                            {chip.sub}
                        </p>
                    </div>
                ))}
            </div>

            {/* Aging bars */}
            <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "12px" }}>
                Distribución por Antigüedad
            </p>
            {aging.map((bucket) => {
                const info = data.aging_buckets[bucket.key] || { count: 0, monto: 0 };
                const pct = data.total_ppd > 0 ? (info.count / data.total_ppd * 100).toFixed(1) : 0;
                return (
                    <div key={bucket.key} style={{ marginBottom: "10px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                            <span style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 600, color: "#334155" }}>
                                {bucket.label}
                            </span>
                            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                                <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "#64748b" }}>
                                    {info.count} UUIDs
                                </span>
                                <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", fontWeight: 700, color: bucket.color }}>
                                    {pct}%
                                </span>
                            </div>
                        </div>
                        <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "3px", overflow: "hidden" }}>
                            <div style={{ width: `${pct}%`, height: "100%", background: bucket.color, borderRadius: "3px", transition: "width 0.6s ease" }} />
                        </div>
                    </div>
                )
            })}

            {/* Alerta si +90d > 20% */}
            {(() => {
                const critico = data.aging_buckets["+90d"]?.count || 0;
                const pct = data.total_ppd > 0 ? critico / data.total_ppd * 100 : 0;
                return pct > 20 ? (
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "14px", padding: "10px 14px", background: "#ef444410", border: "1px solid #ef444430", borderRadius: "10px" }}>
                        <AlertTriangle size={14} color="#ef4444" />
                        <p style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 600, color: "#ef4444" }}>
                            {pct.toFixed(1)}% de UUIDs PPD supera 90 días sin cobro
                        </p>
                    </div>
                ) : null;
            })()}
        </div>
    );
};

const BloqueEficiencia = ({ data }) => (
    <div style={{ background: "white", borderRadius: "20px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #6B84F3" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
            <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#6B84F315", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <FileCheck size={16} color="#6B84F3" />
            </div>
            <div>
                <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                    Eficiencia Documental
                </p>
                <p style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat" }}>
                    Calidad y coherencia de documentos CFDI
                </p>
            </div>
        </div>

        {/* 4 métricas en grid 2x2 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {[
                {
                    label: "NC Excesivas",
                    value: data.nc_excesivas_count,
                    unit: "UUIDs",
                    sub: "NC > 30% del monto original",
                    color: "#FF8A65",
                    icon: AlertTriangle,
                    riesgo: data.nc_excesivas_count > 10
                },
                {
                    label: "Ratio NC / Facturado",
                    value: `${data.ratio_nc_pct}%`,
                    unit: "",
                    sub: data.ratio_nc_pct > 15 ? "⚠️ Supera umbral SAT 15%" : "✓ Dentro del umbral",
                    color: data.ratio_nc_pct > 15 ? "#FF8A65" : "#26A69A",
                    icon: TrendingDown,
                    riesgo: data.ratio_nc_pct > 15
                },
                {
                    label: "Anticipos Pendientes",
                    value: data.anticipos_pendientes.count,
                    unit: "UUIDs",
                    sub: formatMoney(data.anticipos_pendientes.monto, true),
                    color: "#FFCA28",
                    icon: Clock,
                    riesgo: data.anticipos_pendientes.count > 0
                },
                {
                    label: "OTROS Sin Clasificar",
                    value: data.otros_sin_clasificar.count,
                    unit: "UUIDs",
                    sub: formatMoney(data.otros_sin_clasificar.monto, true),
                    color: "#CBD0DA",
                    icon: HelpCircle,
                    riesgo: data.otros_sin_clasificar.count > 0
                }
            ].map((m, i) => {
                const Icon = m.icon;
                return (
                    <div key={i} style={{
                        background: m.riesgo ? `${m.color}08` : "#f8fafc",
                        border: m.riesgo ? `1px solid ${m.color}30` : "1px solid transparent",
                        borderRadius: "14px",
                        padding: "16px"
                    }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                            <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                                {m.label}
                            </p>
                            <Icon size={14} color={m.color} />
                        </div>
                        <p style={{ fontSize: "22px", fontFamily: "JetBrains Mono", fontWeight: 800, color: m.color, lineHeight: 1 }}>
                            {m.value}
                            {m.unit && (
                                <span style={{ fontSize: "11px", color: "#94a3b8", fontWeight: 400, marginLeft: "4px" }}>
                                    {m.unit}
                                </span>
                            )}
                        </p>
                        <p style={{ fontSize: "10px", fontFamily: "Montserrat", color: "#64748b", marginTop: "6px" }}>
                            {m.sub}
                        </p>
                    </div>
                )
            })}
        </div>
    </div>
);

const BloqueRiesgoSAT = ({ data }) => (
    <div style={{ background: "white", borderRadius: "20px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #FF8A65" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#FF8A6515", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Shield size={16} color="#FF8A65" />
                </div>
                <div>
                    <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                        Riesgo Fiscal SAT
                    </p>
                    <p style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat" }}>
                        Indicadores críticos de cumplimiento normativo
                    </p>
                </div>
            </div>

            {/* Chip PPD críticos */}
            {data.ppd_criticos_count > 0 && (
                <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 16px", background: "#FF8A6515", border: "1px solid #FF8A6530", borderRadius: "12px" }}>
                    <AlertTriangle size={14} color="#FF8A65" />
                    <span style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 700, color: "#FF8A65" }}>
                        {data.ppd_criticos_count} PPD sin REP &gt;30 días — {formatMoney(data.ppd_criticos_monto, true)} en riesgo
                    </span>
                </div>
            )}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "20px" }}>
            {/* Top 5 RFCs */}
            <div>
                <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "12px" }}>
                    Concentración por RFC Receptor (Top 5 = {data.concentracion_pct}% del total)
                </p>
                {data.top5_rfc.map((rfc, i) => {
                    const pct = Math.abs(rfc.monto / (data.top5_rfc[0]?.monto || 1) * 100).toFixed(0);
                    return (
                        <div key={i} style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "10px" }}>
                            <span style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", width: "16px", textAlign: "center" }}>
                                {i + 1}
                            </span>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "3px" }}>
                                    <div>
                                        <span style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 600, color: "#334155" }}>
                                            {rfc.nombre || rfc._id}
                                        </span>
                                        <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "#94a3b8", marginLeft: "8px" }}>
                                            {rfc._id}
                                        </span>
                                    </div>
                                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", fontWeight: 700, color: "#6B84F3" }}>
                                        {formatMoney(rfc.monto, true)}
                                    </span>
                                </div>
                                <div style={{ height: "4px", background: "#f1f5f9", borderRadius: "2px", overflow: "hidden" }}>
                                    <div style={{ width: `${pct}%`, height: "100%", background: i === 0 ? "#6B84F3" : `rgba(107,132,243,${0.8 - i * 0.15})`, borderRadius: "2px" }} />
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Gauge de concentración */}
            <div style={{ background: "#f8fafc", borderRadius: "16px", padding: "20px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    Índice de Concentración
                </p>
                <p style={{ fontSize: "48px", fontFamily: "JetBrains Mono", fontWeight: 800, color: data.concentracion_pct > 70 ? "#FF8A65" : data.concentracion_pct > 50 ? "#FFCA28" : "#26A69A", lineHeight: 1 }}>
                    {data.concentracion_pct}%
                </p>
                <p style={{ fontSize: "11px", fontFamily: "Montserrat", color: "#64748b", textAlign: "center" }}>
                    {data.concentracion_pct > 70 ? "⚠️ Concentración alta — riesgo SAT" : data.concentracion_pct > 50 ? "En observación" : "✓ Diversificación adecuada"}
                </p>
            </div>
        </div>
    </div>
);

const BloqueTop10Negativos = ({ data }) => (
    <div style={{ background: "white", borderRadius: "20px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #283593" }}>
        <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>
            Top 10 — Mayor Impacto Negativo
        </p>
        <p style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat", marginBottom: "16px" }}>
            UUIDs que más reducen el saldo neto
        </p>
        {data.map((uuid, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: i < data.length - 1 ? "1px solid #f1f5f9" : "none" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, color: "#cbd5e1", width: "16px" }}>
                        {i + 1}
                    </span>
                    <div>
                        <p style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "#334155" }}>
                            {uuid.uuid}
                        </p>
                        <div style={{ display: "flex", gap: "6px", marginTop: "2px" }}>
                            <span style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: uuid.segmento === "PPD" ? "#785799" : "#6B84F3", background: uuid.segmento === "PPD" ? "#78579915" : "#6B84F315", padding: "1px 6px", borderRadius: "4px" }}>
                                {uuid.segmento}
                            </span>
                            {!uuid.tiene_rep && uuid.segmento === "PPD" && (
                                <span style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#FF8A65", background: "#FF8A6515", padding: "1px 6px", borderRadius: "4px" }}>
                                    SIN REP
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                <span style={{ fontFamily: "JetBrains Mono", fontSize: "13px", fontWeight: 700, color: "#FF8A65" }}>
                    {formatMoney(uuid.saldo_acumulado, true)}
                </span>
            </div>
        ))}
    </div>
);

const BloqueCadenasYFlujo = ({ cadenas, flujo }) => {
    const navigate = useNavigate();
    const { setUUIDTrazabilidad } = useTrazabilidadStore();

    const emit = flujo.find(f => f._id === "EMITIDOS") || { count: 0, monto: 0 };
    const recib = flujo.find(f => f._id === "RECIBIDOS") || { count: 0, monto: 0 };
    const total = emit.count + recib.count;
    const pctE = total ? (emit.count / total * 100).toFixed(1) : 0;
    const pctR = total ? (recib.count / total * 100).toFixed(1) : 0;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Distribución flujo */}
            <div style={{ background: "white", borderRadius: "20px", padding: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #26A69A" }}>
                <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "14px" }}>
                    Distribución Emitidos / Recibidos
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                    {[
                        { label: "EMITIDOS", pct: pctE, count: emit.count, monto: emit.monto, color: "#6B84F3" },
                        { label: "RECIBIDOS", pct: pctR, count: recib.count, monto: recib.monto, color: "#FF8A65" }
                    ].map((f, i) => (
                        <div key={i} style={{ background: "#f8fafc", borderRadius: "12px", padding: "14px", borderLeft: `3px solid ${f.color}` }}>
                            <p style={{ fontSize: "10px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                                {f.label}
                            </p>
                            <p style={{ fontSize: "22px", fontFamily: "JetBrains Mono", fontWeight: 800, color: f.color, lineHeight: 1, margin: "6px 0" }}>
                                {f.pct}%
                            </p>
                            <p style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "#64748b" }}>
                                {f.count.toLocaleString()} UUIDs
                            </p>
                            <p style={{ fontSize: "11px", fontFamily: "JetBrains Mono", fontWeight: 700, color: f.color }}>
                                {formatMoney(f.monto, true)}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* UUIDs cadena larga */}
            <div style={{ background: "white", borderRadius: "20px", padding: "20px", flex: 1, boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderTop: "3px solid #00BCD4" }}>
                <p style={{ fontSize: "12px", fontFamily: "Montserrat", fontWeight: 800, color: "#1e293b", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>
                    Cadenas de Mayor Complejidad
                </p>
                <p style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "Montserrat", marginBottom: "12px" }}>
                    UUIDs con más de 3 eventos de trazabilidad
                </p>
                {cadenas.slice(0, 6).map((c, i) => (
                    <div
                        key={i}
                        onClick={() => {
                            setUUIDTrazabilidad(c._id);
                            navigate('/trazabilidad');
                        }}
                        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 8px", borderBottom: i < 5 ? "1px solid #f1f5f9" : "none", cursor: "pointer", borderRadius: "8px", transition: "background 0.2s" }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f1f5f9'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                        <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "#00BCD4", fontWeight: 700 }}>
                            {c._id}
                        </span>
                        <span style={{ background: "#00BCD415", color: "#00BCD4", fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, padding: "2px 10px", borderRadius: "20px" }}>
                            {c.eventos} eventos
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

// --- Main Component ---
const ContenidoKPIs = ({ data }) => (
    <>
        {/* BLOQUE 1 + 2 — fila superior */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
            <BloqueCarteraPPD data={data.bloque1_cartera_ppd} />
            <BloqueEficiencia data={data.bloque2_eficiencia} />
        </div>

        {/* BLOQUE 3 — ancho completo */}
        <div style={{ marginBottom: "20px" }}>
            <BloqueRiesgoSAT data={data.bloque3_riesgo_sat} />
        </div>

        {/* BLOQUE 4 — 2 columnas */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <BloqueTop10Negativos data={data.bloque4_inteligencia.top10_negativos} />
            <BloqueCadenasYFlujo cadenas={data.bloque4_inteligencia.cadenas_largas} flujo={data.bloque4_inteligencia.dist_flujo} />
        </div>
    </>
);

const KPIsTab = () => {
    const { filters } = useFilterStore();
    const periodoActivo = `${filters.year}-${String(filters.month).padStart(2, "0")}`;

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!periodoActivo) return;
        setLoading(true);
        setData(null);
        api.get(`/api/kpis/resumen?periodo=${periodoActivo}`)
            .then(res => {
                setData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [periodoActivo]);

    const formatPeriodo = (p) => {
        if (!p) return "";
        const [anio, mes] = p.split("-");
        const meses = {
            "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
            "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
            "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        };
        return `${meses[mes]} ${anio}`;
    };

    return (
        <div style={{ padding: "0 4px", maxWidth: "1200px", margin: "0 auto" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 20px", background: "white", borderRadius: "12px", marginBottom: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", borderLeft: "4px solid #6B84F3" }}>
                <Calendar size={16} color="#6B84F3" />
                <span style={{ fontSize: "11px", fontFamily: "Montserrat", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase" }}>Período Fiscal:</span>
                <span style={{ fontSize: "15px", fontFamily: "JetBrains Mono", fontWeight: 800, color: "#6B84F3" }}>{periodoActivo}</span>
                <span style={{ fontSize: "13px", fontFamily: "Montserrat", color: "#64748b" }}>{formatPeriodo(periodoActivo)}</span>
            </div>

            {loading ? (
                <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "300px" }}>
                    <div style={{ width: "40px", height: "40px", border: "3px solid #f1f5f9", borderTop: "3px solid #6B84F3", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                    <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                </div>
            ) : data ? (
                <ContenidoKPIs data={data} />
            ) : null}
        </div>
    );
};

export default KPIsTab;
