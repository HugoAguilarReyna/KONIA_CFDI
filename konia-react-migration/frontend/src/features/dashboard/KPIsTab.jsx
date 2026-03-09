/* eslint-disable react/prop-types */
/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, AreaChart, Area, Legend,
    ReferenceLine
} from "recharts";
import {
    TrendingUp, TrendingDown, Layers, DollarSign, FileText,
    Clock, Activity, Shield, AlertTriangle, CheckCircle,
    Percent, Receipt, Package, BarChart2, Briefcase,
    ArrowUpRight, ArrowDownRight, Zap, Users, FileX,
    Timer, Target, FileMinus, FileCheck, AlertCircle,
    User, Building2
} from 'lucide-react';
import Plot from 'react-plotly.js';
import api from '../../api/axiosConfig';
import useFilterStore from '../../stores/useFilterStore';
import { useTrazabilidadStore } from '../../stores/useTrazabilidadStore';

/* ══════════════════════════════════════════════════════════════════
   ESTILOS — KONIA: light, clean, indigo/teal
══════════════════════════════════════════════════════════════════ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --indigo:  #5b6af0;
  --violet:  #7c3aed;
  --teal:    #0d9488;
  --orange:  #f97316;
  --rose:    #f43f5e;
  --amber:   #f59e0b;
  --emerald: #10b981;
  --slate:   #64748b;
  --bg:      #f4f6fb;
  --surface: #ffffff;
  --border:  rgba(99,102,241,0.1);
}

@keyframes fadeUp   { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
@keyframes barIn    { from{transform:scaleX(0)} to{transform:scaleX(1)} }
@keyframes countUp  { from{opacity:0;transform:scale(.8)} to{opacity:1;transform:scale(1)} }
@keyframes pulseGreen { 0%,100%{opacity:1} 50%{opacity:.4} }
@keyframes slideIn  { from{opacity:0;transform:translateX(-8px)} to{opacity:1;transform:translateX(0)} }

.konia-card {
  background: var(--surface);
  border-radius: 18px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 12px rgba(91,106,240,.05);
  overflow: hidden;
}
.konia-card-hover {
  transition: transform .2s ease, box-shadow .2s ease;
}
.konia-card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(91,106,240,.1);
}
.konia-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 9px; border-radius: 20px;
  font-size: 10px; font-weight: 700; letter-spacing: .04em;
  font-family: 'JetBrains Mono', monospace;
}
.konia-badge-ppd  { background: rgba(91,106,240,.1);  color: #5b6af0; }
.konia-badge-pue  { background: rgba(13,148,136,.1);   color: #0d9488; }
.konia-badge-nr   { background: rgba(249,115,22,.1);   color: #f97316; }
.konia-badge-warn { background: rgba(244,63,94,.1);    color: #f43f5e; }
.konia-btn-toggle {
  padding: 5px 14px; border-radius: 20px; font-size: 11px;
  font-weight: 700; cursor: pointer; border: none; transition: all .2s;
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.konia-btn-active   { background: var(--indigo); color: white; box-shadow: 0 4px 12px rgba(91,106,240,.3); }
.konia-btn-inactive { background: rgba(91,106,240,.07); color: var(--slate); }
.konia-section-title {
  font-size: 11px; font-weight: 800; letter-spacing: .1em;
  text-transform: uppercase; color: var(--slate);
}
.konia-divider { height: 1px; background: rgba(99,102,241,.07); margin: 0 20px; }
.accent-indigo { border-top: 3px solid var(--indigo); }
.accent-teal   { border-top: 3px solid var(--teal);   }
.accent-orange { border-top: 3px solid var(--orange);  }
.accent-rose   { border-top: 3px solid var(--rose);    }
.accent-violet { border-top: 3px solid var(--violet);  }
`;

/* ══════════════════════════════════════════════════════════════════
   HELPERS
══════════════════════════════════════════════════════════════════ */
const fmt = (n, dec = 2) => {
    if (n == null) return "$0";
    const abs = Math.abs(n);
    const sign = n < 0 ? "-" : "";
    if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(1)}B`;
    if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(1)}M`;
    if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(1)}K`;
    return `${sign}$${abs.toFixed(dec)}`;
};

const fmtFull = n => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(n ?? 0);
const pct = n => `${Number(n ?? 0).toFixed(1)}%`;

/* Icon bubble — matches KONIA reference design */
const IconBubble = ({ icon: Icon, color, bg, size = 18 }) => (
    <div style={{
        width: 36, height: 36, borderRadius: 10,
        background: bg || `${color}18`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0
    }}>
        <Icon size={size} color={color} strokeWidth={1.8} />
    </div>
);

const Mono = ({ children, color, size = 13, weight = 600 }) => (
    <span style={{ fontFamily: "'JetBrains Mono',monospace", color: color || "inherit", fontSize: size, fontWeight: weight }}>
        {children}
    </span>
);

/* Tooltip limpio para charts */
const FiscalTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div style={{
            background: "white", border: "1px solid rgba(99,102,241,.15)",
            borderRadius: 12, padding: "12px 16px", boxShadow: "0 8px 24px rgba(0,0,0,.1)", minWidth: 200
        }}>
            <p style={{ fontSize: 11, fontWeight: 800, color: "#5b6af0", marginBottom: 8, letterSpacing: ".06em" }}>{label}</p>
            {payload.map((p, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: 16, marginTop: 3 }}>
                    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: p.color, flexShrink: 0 }} />
                        <span style={{ fontSize: 10, color: "#64748b", fontWeight: 600 }}>{p.name}</span>
                    </div>
                    <Mono size={11} color="#1e293b">
                        {typeof p.value === "number" && Math.abs(p.value) > 1000 ? fmt(p.value, 0) : p.value}
                    </Mono>
                </div>
            ))}
        </div>
    );
};

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 1 — KPIs SUPERIORES
══════════════════════════════════════════════════════════════════ */
const KPISuperiores = ({ modo, setModo, data }) => {
    const isCliente = modo === "cliente";
    const cfdiCount = isCliente ? (data.totalCFDIs_cliente ?? 0) : (data.totalCFDIs_proveedor ?? 0);
    const monto = isCliente ? (data.montoTotal_cliente ?? 0) : (data.montoTotal_proveedor ?? 0);

    const kpis = [
        {
            label: "Deducibilidad CFDI",
            value: pct(data.deducibilidad_pct ?? 0),
            sub: "Facturas con requisitos SAT",
            LucideIcon: FileCheck,
            color: (data.deducibilidad_pct ?? 0) >= 90 ? "#10b981" : "#f59e0b",
            bg: (data.deducibilidad_pct ?? 0) >= 90 ? "rgba(16,185,129,.07)" : "rgba(245,158,11,.07)",
        },
        {
            label: "Tasa Cancelación",
            value: pct(data.tasaCancelacion ?? 0),
            sub: `${data.cfdisCancelados ?? 0} CFDIs cancelados`,
            LucideIcon: FileX,
            color: (data.tasaCancelacion ?? 0) > 5 ? "#f43f5e" : "#f59e0b",
            bg: "rgba(249,115,22,.07)",
        },
        {
            label: "Eficiencia de Cobro",
            value: pct(data.eficienciaRecup ?? 0),
            sub: "Recuperación < 30 días PPD",
            LucideIcon: Zap,
            color: "#5b6af0",
            bg: "rgba(91,106,240,.07)",
        },
        {
            label: "Posición Fiscal Neta",
            value: fmt(data.saldoNeto ?? 0),
            sub: (data.posicionFiscal ?? "FAVOR") === "FAVOR" ? "✓ Saldo a favor" : "⚠ Saldo a cargo",
            LucideIcon: Activity,
            color: (data.posicionFiscal ?? "FAVOR") === "FAVOR" ? "#0d9488" : "#f43f5e",
            bg: (data.posicionFiscal ?? "FAVOR") === "FAVOR" ? "rgba(13,148,136,.07)" : "rgba(244,63,94,.07)",
        },
        {
            label: "Discrepancia Fiscal",
            value: pct(data.discrepancia_pct ?? 0),
            sub: "Diferencia XML vs contabilidad",
            LucideIcon: AlertCircle,
            color: (data.discrepancia_pct ?? 0) < 2 ? "#f59e0b" : "#f43f5e",
            bg: "rgba(245,158,11,.07)",
        },
        {
            label: "REP por Vencer",
            value: `${data.diasProxVencer ?? 0}d`,
            sub: "Días para vencimiento REP",
            LucideIcon: Timer,
            color: (data.diasProxVencer ?? 0) <= 7 ? "#f43f5e" : "#f59e0b",
            bg: (data.diasProxVencer ?? 0) <= 7 ? "rgba(244,63,94,.07)" : "rgba(245,158,11,.07)",
        },
    ];

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {/* Fila 1: Toggle + CFDIs + Monto */}
            <div style={{ display: "grid", gridTemplateColumns: "auto 1fr 1fr", gap: 12, alignItems: "stretch" }}>
                {/* Toggle cliente/proveedor */}
                <div className="konia-card" style={{
                    padding: "18px 22px",
                    background: "linear-gradient(135deg,rgba(91,106,240,.04),rgba(124,58,237,.04))",
                    borderTop: "3px solid var(--indigo)",
                    animation: "fadeUp .4s ease both"
                }}>
                    <p className="konia-section-title" style={{ marginBottom: 14 }}>Vista</p>
                    <div style={{ display: "flex", gap: 6, marginBottom: 14 }}>
                        {["cliente", "proveedor"].map(m => (
                            <button key={m} className={`konia-btn-toggle ${modo === m ? "konia-btn-active" : "konia-btn-inactive"}`}
                                onClick={() => setModo(m)}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                                    {m === "cliente"
                                        ? <><User size={11} strokeWidth={2} /> Cliente</>
                                        : <><Building2 size={11} strokeWidth={2} /> Proveedor</>}
                                </span>
                            </button>
                        ))}
                    </div>
                    <div style={{ display: "flex", gap: 16 }}>
                        <div>
                            <p style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: ".06em", marginBottom: 3 }}>ROL FISCAL</p>
                            <Mono size={13} color="#0d9488" weight={700}>
                                {modo === "cliente" ? "EMISOR" : "RECEPTOR"}
                            </Mono>
                        </div>
                    </div>
                </div>

                {/* Conteo CFDIs */}
                <div className="konia-card konia-card-hover accent-indigo" style={{ padding: "18px 24px", animation: "fadeUp .4s ease .06s both" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                        <p className="konia-section-title">Conteo de CFDIs</p>
                        <IconBubble icon={Receipt} color="#5b6af0" bg="rgba(91,106,240,.1)" size={16} />
                    </div>
                    <Mono size={38} color="#5b6af0" weight={700} style={{ display: "block", lineHeight: 1, animation: "countUp .5s ease .1s both" }}>
                        {cfdiCount.toLocaleString("es-MX")}
                    </Mono>
                    <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 6 }}>
                        CFDIs como {modo === "cliente" ? "emisor (cliente)" : "receptor (proveedor)"}
                    </p>
                    <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
                        <span className="konia-chip konia-badge-ppd">PPD</span>
                        <span className="konia-chip konia-badge-pue">PUE</span>
                    </div>
                </div>

                {/* Monto total */}
                <div className="konia-card konia-card-hover accent-teal" style={{ padding: "18px 24px", animation: "fadeUp .4s ease .12s both" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                        <p className="konia-section-title">Monto Total del Período</p>
                        <IconBubble icon={DollarSign} color="#0d9488" bg="rgba(13,148,136,.1)" size={16} />
                    </div>
                    <Mono size={30} color={monto < 0 ? "#f43f5e" : "#0d9488"} weight={700} style={{ display: "block", lineHeight: 1.1, animation: "countUp .5s ease .15s both" }}>
                        {fmt(monto)}
                    </Mono>
                    <p style={{ fontSize: 10, color: "#94a3b8", marginTop: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                        {fmtFull(monto)}
                    </p>
                    <div style={{ marginTop: 12, padding: "6px 10px", borderRadius: 8, background: monto < 0 ? "rgba(244,63,94,.07)" : "rgba(13,148,136,.07)" }}>
                        <p style={{ fontSize: 10, fontWeight: 700, color: monto < 0 ? "#f43f5e" : "#0d9488" }}>
                            {monto < 0 ? "⚠ Posición pasiva" : "✓ Posición activa"}
                        </p>
                    </div>
                </div>
            </div>

            {/* Fila 2: 6 KPIs fiscales */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", gap: 10 }}>
                {kpis.map((k, i) => (
                    <div key={i} className="konia-card konia-card-hover" style={{
                        padding: "14px 16px",
                        borderTop: `2px solid ${k.color}`,
                        animation: `fadeUp .4s ease ${i * 0.06}s both`
                    }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                            <p style={{ fontSize: 9, fontWeight: 800, color: "#94a3b8", letterSpacing: ".08em", textTransform: "uppercase", lineHeight: 1.3 }}>{k.label}</p>
                            {k.LucideIcon && <k.LucideIcon size={14} color={k.color} strokeWidth={1.8} style={{ opacity: .75, flexShrink: 0 }} />}
                        </div>
                        <Mono size={20} color={k.color} weight={700} style={{ display: "block", marginBottom: 4 }}>{k.value}</Mono>
                        <div style={{ background: k.bg, borderRadius: 6, padding: "3px 6px", marginTop: 4 }}>
                            <p style={{ fontSize: 9, color: k.color, fontWeight: 600, lineHeight: 1.3 }}>{k.sub}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 2A — GRÁFICA DE CAJA (BOX PLOT) PREMIUM
══════════════════════════════════════════════════════════════════ */
const BoxPlotHistorico = ({ historico }) => {
    if (!historico || historico.length === 0) return null;

    // Extracting data arrays for the box plot
    const saldosPPD = historico.map(d => d.saldoPPD || 0);
    const saldosPUE = historico.map(d => d.saldoPUE || 0);

    const commonLayout = {
        title: false,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 5, r: 10, l: 45, b: 25 },
        height: 180,
        font: { family: "'Plus Jakarta Sans', sans-serif", color: "#64748b" },
        xaxis: {
            showgrid: false,
            zeroline: false,
            tickfont: { size: 9, family: "'Plus Jakarta Sans', sans-serif" }
        },
        yaxis: {
            gridcolor: 'rgba(99,102,241,.05)',
            zerolinecolor: 'rgba(99,102,241,.15)',
            tickfont: { size: 9, family: "'JetBrains Mono', monospace" },
            tickprefix: '$'
        },
        showlegend: false,
    };

    return (
        <div className="konia-card" style={{ padding: "20px 24px", borderLeft: "4px solid #7c3aed", animation: "fadeUp .5s ease .15s both", marginBottom: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 15 }}>
                <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <IconBubble icon={BarChart2} color="#7c3aed" bg="rgba(124,58,237,.1)" size={16} />
                        <p className="konia-section-title" style={{ marginBottom: 0 }}>Distribución de Saldos (Box Plot)</p>
                    </div>
                    <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>Análisis de varianza y valores atípicos mensuales (PPD vs PUE)</p>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div>
                    <p style={{ fontSize: 10, fontWeight: 700, color: "#5b6af0", textAlign: "center", marginBottom: 8, letterSpacing: "0.05em" }}>SALDO PPD</p>
                    <Plot
                        data={[{
                            y: saldosPPD,
                            type: 'box',
                            name: 'PPD',
                            marker: { color: '#5b6af0' },
                            boxpoints: 'all', jitter: 0.3, pointpos: -1.8, line: { width: 1.5 },
                            fillcolor: 'rgba(91,106,240,0.1)'
                        }]}
                        layout={commonLayout}
                        config={{ displayModeBar: false, responsive: true }}
                        style={{ width: "100%", height: "180px" }}
                    />
                </div>
                <div>
                    <p style={{ fontSize: 10, fontWeight: 700, color: "#0d9488", textAlign: "center", marginBottom: 8, letterSpacing: "0.05em" }}>SALDO PUE</p>
                    <Plot
                        data={[{
                            y: saldosPUE,
                            type: 'box',
                            name: 'PUE',
                            marker: { color: '#0d9488' },
                            boxpoints: 'all', jitter: 0.3, pointpos: -1.8, line: { width: 1.5 },
                            fillcolor: 'rgba(13,148,136,0.1)'
                        }]}
                        layout={commonLayout}
                        config={{ displayModeBar: false, responsive: true }}
                        style={{ width: "100%", height: "180px" }}
                    />
                </div>
            </div>
        </div>
    );
};

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 2 — GRÁFICA HISTÓRICA
══════════════════════════════════════════════════════════════════ */
const GraficaHistorico = ({ historico }) => {
    const [vista, setVista] = useState("saldos");

    if (!historico || historico.length === 0) return null;

    return (
        <div className="konia-card" style={{ padding: "22px 24px", borderLeft: "4px solid #5b6af0", animation: "fadeUp .5s ease .2s both" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <div>
                    <p className="konia-section-title" style={{ marginBottom: 2 }}>Evolución de Saldos (Histórico)</p>
                    <p style={{ fontSize: 11, color: "#94a3b8" }}>Saldo PPD, PUE y Volumen de CFDIs</p>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                    {[["saldos", "Saldos"], ["volumen", "Volumen"], ["combinada", "Combinada"]].map(([v, l]) => (
                        <button key={v} className={`konia-btn-toggle ${vista === v ? "konia-btn-active" : "konia-btn-inactive"}`}
                            style={{ fontSize: 10 }} onClick={() => setVista(v)}>{l}</button>
                    ))}
                </div>
            </div>

            <ResponsiveContainer width="100%" height={220}>
                <ComposedChart data={historico} margin={{ top: 10, right: 60, left: 20, bottom: 0 }}>
                    <defs>
                        <linearGradient id="gradPPD" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#5b6af0" stopOpacity={.15} />
                            <stop offset="95%" stopColor="#5b6af0" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid stroke="rgba(99,102,241,.07)" strokeDasharray="4 4" vertical={false} />
                    <XAxis dataKey="periodo"
                        tick={{ fontSize: 10, fontFamily: "'JetBrains Mono',monospace", fill: "#94a3b8" }}
                        axisLine={false} tickLine={false} />
                    <YAxis yAxisId="left" orientation="left"
                        tickFormatter={v => `${(v / 1e6).toFixed(0)}M`}
                        tick={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", fill: "#94a3b8" }}
                        axisLine={false} tickLine={false}
                        hide={vista === "volumen"} />
                    <YAxis yAxisId="right" orientation="right"
                        tick={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", fill: "#94a3b8" }}
                        axisLine={false} tickLine={false}
                        hide={vista === "saldos"} />
                    <Tooltip content={<FiscalTooltip />} />
                    <ReferenceLine yAxisId="left" y={0} stroke="rgba(99,102,241,.2)" strokeDasharray="3 3" />
                    {(vista === "volumen" || vista === "combinada") && (
                        <>
                            <Bar yAxisId="right" dataKey="emitidos" name="Emitidos" fill="rgba(91,106,240,.25)" stroke="#5b6af0" strokeWidth={1} radius={[3, 3, 0, 0]} />
                            <Bar yAxisId="right" dataKey="recibidos" name="Recibidos" fill="rgba(249,115,22,.2)" stroke="#f97316" strokeWidth={1} radius={[3, 3, 0, 0]} />
                        </>
                    )}
                    {(vista === "saldos" || vista === "combinada") && (
                        <Area yAxisId="left" type="monotone" dataKey="saldoPPD"
                            name="Saldo PPD" stroke="#5b6af0" strokeWidth={2.5}
                            fill="url(#gradPPD)"
                            dot={{ fill: "#5b6af0", r: 4, strokeWidth: 2, stroke: "white" }}
                            activeDot={{ r: 6, fill: "#5b6af0" }} />
                    )}
                    {(vista === "saldos" || vista === "combinada") && (
                        <Line yAxisId="left" type="monotone" dataKey="saldoPUE"
                            name="Saldo PUE" stroke="#0d9488" strokeWidth={2} strokeDasharray="5 3"
                            dot={{ fill: "#0d9488", r: 4, strokeWidth: 2, stroke: "white" }}
                            activeDot={{ r: 6, fill: "#0d9488" }} />
                    )}
                </ComposedChart>
            </ResponsiveContainer>

            {/* Mini resumen periodos */}
            <div style={{ display: "grid", gridTemplateColumns: `repeat(${historico.length},1fr)`, gap: 8, marginTop: 16 }}>
                {historico.map((h, i) => {
                    const delta = i > 0 && HISTORICO_DATA[i - 1]
                        ? ((h.saldoPPD - historico[i - 1].saldoPPD) / Math.abs(historico[i - 1].saldoPPD || 1) * 100)
                        : null;
                    const isActual = i === historico.length - 1;
                    return (
                        <div key={i} style={{
                            padding: "8px 10px", borderRadius: 10, textAlign: "center",
                            background: isActual ? "rgba(91,106,240,.07)" : "rgba(100,116,139,.04)",
                            border: isActual ? "1px solid rgba(91,106,240,.2)" : "1px solid transparent"
                        }}>
                            <Mono size={9} color={isActual ? "#5b6af0" : "#94a3b8"} weight={700}>{h.periodo}</Mono>
                            <p style={{ fontSize: 11, fontWeight: 700, color: "#1e293b", marginTop: 2 }}>{fmt(h.saldoPPD)}</p>
                            {delta !== null && (
                                <p style={{ fontSize: 9, fontWeight: 700, color: delta < 0 ? "#f43f5e" : "#10b981", marginTop: 1 }}>
                                    {delta < 0 ? "▼" : "▲"} {Math.abs(delta).toFixed(1)}%
                                </p>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// Small helper needed inside GraficaHistorico — just holds reference
let HISTORICO_DATA = [];

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 3 — SALUD DE CARTERA + EFICIENCIA DOCUMENTAL
══════════════════════════════════════════════════════════════════ */
const SaludEficiencia = ({ data }) => {
    const aging = data.aging || [
        { rango: "0-30 días", uuids: 0, pct: 0.0, color: "#10b981" },
        { rango: "31-60 días", uuids: 0, pct: 0.0, color: "#f59e0b" },
        { rango: "61-90 días", uuids: 0, pct: 0.0, color: "#f97316" },
        { rango: "+90 días", uuids: 0, pct: 0.0, color: "#f43f5e" },
    ];

    return (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            {/* Salud de Cartera PPD */}
            <div className="konia-card" style={{ borderTop: "3px solid #5b6af0", animation: "fadeUp .5s ease .25s both" }}>
                <div style={{ padding: "18px 20px 14px" }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 4 }}>
                        <IconBubble icon={Clock} color="#5b6af0" bg="rgba(91,106,240,.1)" size={17} />
                        <div>
                            <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b" }}>SALUD DE CARTERA PPD</p>
                            <p style={{ fontSize: 11, color: "#94a3b8" }}>Antigüedad de saldo pendiente de cobro</p>
                        </div>
                    </div>
                </div>
                <div className="konia-divider" />
                <div style={{ padding: "14px 20px" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginBottom: 16 }}>
                        {[
                            { l: "DSO PROMEDIO", v: `${data.dsoDias ?? 0}d`, sub: "días promedio de cobro", c: "#7c3aed" },
                            { l: "SIN REP", v: data.sinREP_count ?? 0, sub: fmtFull(data.sinREP_monto ?? 0), c: "#f97316" },
                            { l: "RECUPERACIÓN", v: pct(data.recuperacion_pct ?? 0), sub: "con complemento pago", c: "#10b981" },
                        ].map((item, i) => (
                            <div key={i} style={{ background: "rgba(100,116,139,.04)", borderRadius: 12, padding: "12px", borderLeft: `3px solid ${item.c}` }}>
                                <p style={{ fontSize: 9, fontWeight: 800, color: "#94a3b8", letterSpacing: ".07em", marginBottom: 6 }}>{item.l}</p>
                                <Mono size={22} color={item.c} weight={700}>{item.v}</Mono>
                                <p style={{ fontSize: 9, color: "#94a3b8", marginTop: 3 }}>{item.sub}</p>
                            </div>
                        ))}
                    </div>
                    <p className="konia-section-title" style={{ marginBottom: 10 }}>Distribución por Antigüedad</p>
                    {aging.map((a, i) => (
                        <div key={i} style={{
                            display: "flex", justifyContent: "space-between", alignItems: "center",
                            padding: "7px 0", borderBottom: i < aging.length - 1 ? "1px solid rgba(99,102,241,.06)" : "none"
                        }}>
                            <span style={{ fontSize: 12, color: "#475569", fontWeight: 500 }}>{a.rango}</span>
                            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                                <Mono size={11} color="#64748b">{a.uuids} UUIDs</Mono>
                                <Mono size={11} color={a.uuids > 0 ? a.color : "#94a3b8"} weight={700}>{Number(a.pct ?? 0).toFixed(1)}%</Mono>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Eficiencia Documental */}
            <div className="konia-card" style={{ borderTop: "3px solid #0d9488", animation: "fadeUp .5s ease .3s both" }}>
                <div style={{ padding: "18px 20px 14px" }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 4 }}>
                        <IconBubble icon={FileText} color="#0d9488" bg="rgba(13,148,136,.1)" size={17} />
                        <div>
                            <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b" }}>EFICIENCIA DOCUMENTAL</p>
                            <p style={{ fontSize: 11, color: "#94a3b8" }}>Calidad y coherencia de documentos CFDI</p>
                        </div>
                    </div>
                </div>
                <div className="konia-divider" />
                <div style={{ padding: "14px 20px" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                        {[
                            { l: "NC EXCESIVAS", LucideIcon: AlertTriangle, v: `${data.ncExcesivas ?? 0} UUIDs`, sub: "NC > 30% del monto original", color: "#f43f5e", alert: (data.ncExcesivas ?? 0) > 0 },
                            { l: "RATIO NC / FACTURADO", LucideIcon: Percent, v: pct(data.ratioNC ?? 0), sub: "✓ Dentro del umbral", color: "#0d9488", alert: false },
                            { l: "ANTICIPOS PENDIENTES", LucideIcon: Timer, v: `${data.anticipos_n ?? 0} UUIDs`, sub: fmtFull(data.anticipos_m ?? 0), color: "#f59e0b", alert: (data.anticipos_n ?? 0) > 0 },
                            { l: "OTROS SIN CLASIFICAR", LucideIcon: Package, v: `${data.otrosSinClass ?? 0} UUIDs`, sub: fmtFull(data.otrosMonto ?? 0), color: "#94a3b8", alert: false },
                        ].map((item, i) => (
                            <div key={i} style={{
                                background: item.alert ? "rgba(244,63,94,.04)" : "rgba(100,116,139,.04)",
                                borderRadius: 12, padding: "14px",
                                border: `1px solid ${item.alert ? "rgba(244,63,94,.15)" : "transparent"}`
                            }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                                    <p style={{ fontSize: 9, fontWeight: 800, color: "#94a3b8", letterSpacing: ".07em", lineHeight: 1.3 }}>{item.l}</p>
                                    {item.LucideIcon && <item.LucideIcon size={14} color={item.color} strokeWidth={1.8} style={{ opacity: .8, flexShrink: 0 }} />}
                                </div>
                                <Mono size={18} color={item.color} weight={700}>{item.v}</Mono>
                                <p style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>{item.sub}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 4 — RIESGO SAT + DISTRIBUCIÓN + CADENAS
══════════════════════════════════════════════════════════════════ */
const RiesgoDistribucion = ({ data }) => (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {/* Riesgo Fiscal SAT */}
        <div className="konia-card" style={{ borderTop: "3px solid #f43f5e", animation: "fadeUp .5s ease .35s both" }}>
            <div style={{ padding: "18px 20px 14px" }}>
                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <IconBubble icon={Shield} color="#f43f5e" bg="rgba(244,63,94,.08)" size={17} />
                    <div>
                        <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b" }}>RIESGO FISCAL SAT</p>
                        <p style={{ fontSize: 11, color: "#94a3b8" }}>Indicadores críticos de cumplimiento normativo</p>
                    </div>
                </div>
            </div>
            <div className="konia-divider" />
            <div style={{ padding: "16px 20px" }}>
                <p style={{ fontSize: 10, fontWeight: 800, color: "#94a3b8", letterSpacing: ".08em", marginBottom: 12 }}>
                    CONCENTRACIÓN POR RFC RECEPTOR (TOP 5 = {data.concentracion_pct ?? 0}% DEL TOTAL)
                </p>
                <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                    <div style={{ flex: 1 }}>
                        <div style={{ height: 8, background: "rgba(100,116,139,.1)", borderRadius: 4, overflow: "hidden", marginBottom: 6 }}>
                            <div style={{
                                width: `${Math.min(data.concentracion_pct ?? 0, 100)}%`, height: "100%",
                                background: (data.concentracion_pct ?? 0) > 50 ? "#f43f5e" : (data.concentracion_pct ?? 0) > 25 ? "#f59e0b" : "#10b981",
                                borderRadius: 4, animation: "barIn .8s ease both", transformOrigin: "left"
                            }} />
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ fontSize: 9, color: "#94a3b8" }}>Diversificado</span>
                            <span style={{ fontSize: 9, color: "#94a3b8" }}>Concentrado</span>
                        </div>
                    </div>
                    <div style={{ textAlign: "center", minWidth: 80 }}>
                        <p style={{ fontSize: 9, fontWeight: 800, color: "#94a3b8", letterSpacing: ".08em", marginBottom: 2 }}>ÍNDICE</p>
                        <Mono size={28} color={(data.concentracion_pct ?? 0) < 30 ? "#0d9488" : "#f43f5e"} weight={700}>
                            {pct(data.indiceConcentracion ?? 0)}
                        </Mono>
                        <p style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>✓ Diversificación adecuada</p>
                    </div>
                </div>
                <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 8 }}>
                    <p style={{ fontSize: 10, fontWeight: 800, color: "#94a3b8", letterSpacing: ".08em", marginBottom: 4 }}>ALERTAS NORMATIVAS</p>
                    {[
                        { label: "CFDIs sin complemento de pago", v: data.sinREP_count ?? 0, warn: (data.sinREP_count ?? 0) > 0 },
                        { label: "Discrepancia XML vs contabilidad", v: `${data.discrepancia_pct ?? 0}%`, warn: (data.discrepancia_pct ?? 0) > 2 },
                        { label: "Notas de crédito sobre umbral", v: `${data.ncExcesivas ?? 0} NCs`, warn: (data.ncExcesivas ?? 0) > 0 },
                        { label: "CFDIs cancelados en período", v: data.cfdisCancelados ?? 0, warn: (data.tasaCancelacion ?? 0) > 5 },
                    ].map((a, i) => (
                        <div key={i} style={{
                            display: "flex", justifyContent: "space-between", alignItems: "center",
                            padding: "7px 10px", borderRadius: 8,
                            background: a.warn ? "rgba(244,63,94,.05)" : "rgba(100,116,139,.04)"
                        }}>
                            <span style={{ fontSize: 11, color: a.warn ? "#f43f5e" : "#64748b", fontWeight: 500 }}>{a.label}</span>
                            <span className="konia-chip" style={{
                                background: a.warn ? "rgba(244,63,94,.12)" : "rgba(16,185,129,.1)",
                                color: a.warn ? "#f43f5e" : "#10b981"
                            }}>{a.v}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>

        {/* Distribución + Cadenas */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div className="konia-card" style={{ borderTop: "3px solid #7c3aed", padding: "18px 20px", animation: "fadeUp .5s ease .38s both" }}>
                <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b", marginBottom: 14 }}>DISTRIBUCIÓN EMITIDOS / RECIBIDOS</p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    {[
                        { l: "EMITIDOS", pct: data.emitidos_pct ?? 0, n: data.emitidos_n ?? 0, m: data.emitidos_m ?? 0, c: "#5b6af0", bg: "91,106,240" },
                        { l: "RECIBIDOS", pct: data.recibidos_pct ?? 0, n: data.recibidos_n ?? 0, m: data.recibidos_m ?? 0, c: "#f97316", bg: "249,115,22" },
                    ].map((d, i) => (
                        <div key={i} style={{
                            background: `rgba(${d.bg},.05)`, borderRadius: 12, padding: "14px",
                            border: `1px solid rgba(${d.bg},.12)`
                        }}>
                            <p style={{ fontSize: 10, fontWeight: 800, color: "#94a3b8", letterSpacing: ".08em", marginBottom: 6 }}>{d.l}</p>
                            <Mono size={28} color={d.c} weight={700}>{d.pct.toFixed(1)}%</Mono>
                            <p style={{ fontSize: 10, color: "#64748b", marginTop: 4 }}>{d.n.toLocaleString("es-MX")} UUIDs</p>
                            <Mono size={11} color={d.c}>{fmtFull(d.m)}</Mono>
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: 12, height: 8, borderRadius: 4, overflow: "hidden", display: "flex" }}>
                    <div style={{ width: `${data.emitidos_pct ?? 50}%`, background: "#5b6af0", transition: "width .6s ease" }} />
                    <div style={{ width: `${data.recibidos_pct ?? 50}%`, background: "#f97316" }} />
                </div>
            </div>

            <div className="konia-card" style={{ borderTop: "3px solid #0d9488", padding: "18px 20px", flex: 1, animation: "fadeUp .5s ease .42s both" }}>
                <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b", marginBottom: 4 }}>CADENAS DE MAYOR COMPLEJIDAD</p>
                <p style={{ fontSize: 11, color: "#94a3b8", marginBottom: 14 }}>UUIDs con más de 3 eventos de trazabilidad</p>
                {(data.cadenas || []).length > 0
                    ? (data.cadenas || []).map((c, i) => (
                        <div key={i} style={{
                            display: "flex", justifyContent: "space-between", alignItems: "center",
                            padding: "10px 12px", borderRadius: 10,
                            background: "rgba(13,148,136,.05)", border: "1px solid rgba(13,148,136,.15)",
                            animation: `slideIn .4s ease ${i * .1}s both`, marginBottom: 6
                        }}>
                            <Mono size={10} color="#0d9488" weight={500}>{c.uuid}</Mono>
                            <span className="konia-chip" style={{ background: "rgba(91,106,240,.1)", color: "#5b6af0" }}>
                                {c.eventos} eventos
                            </span>
                        </div>
                    ))
                    : <p style={{ fontSize: 11, color: "#94a3b8" }}>Sin cadenas de alta complejidad</p>
                }
            </div>
        </div>
    </div>
);

/* ══════════════════════════════════════════════════════════════════
   BLOQUE 5 — TOP 10 MAYOR IMPACTO NEGATIVO
══════════════════════════════════════════════════════════════════ */
const Top10 = ({ data }) => {
    const top10 = data.top10 || [];
    if (top10.length === 0) return null;

    return (
        <div className="konia-card" style={{ borderTop: "3px solid #f97316", animation: "fadeUp .5s ease .45s both" }}>
            <div style={{ padding: "18px 24px 14px" }}>
                <p style={{ fontSize: 13, fontWeight: 800, color: "#1e293b" }}>TOP 10 — MAYOR IMPACTO NEGATIVO</p>
                <p style={{ fontSize: 11, color: "#94a3b8" }}>UUIDs que más reducen el saldo neto · Posibles riesgos de deducción</p>
            </div>
            <div className="konia-divider" />
            <div style={{ padding: "8px 0" }}>
                {top10.map((item, i) => {
                    const maxAbs = Math.abs(top10[0].monto || 1);
                    const barW = Math.abs(item.monto) / maxAbs * 100;
                    const tipo = item.tipo || item.segmento || "PPD";
                    const sinRep = item.sinRep ?? item.sin_rep ?? false;
                    return (
                        <div key={i} style={{
                            display: "grid", gridTemplateColumns: "28px 1fr auto", gap: 12,
                            padding: "10px 24px", alignItems: "center",
                            background: i % 2 === 0 ? "transparent" : "rgba(100,116,139,.02)",
                            borderBottom: i < top10.length - 1 ? "1px solid rgba(99,102,241,.05)" : "none",
                            animation: `slideIn .4s ease ${i * .04}s both`
                        }}>
                            <Mono size={12} color="#94a3b8" weight={700}>{i + 1}</Mono>
                            <div>
                                <Mono size={10} color="#475569" weight={500} style={{ display: "block", marginBottom: 4 }}>
                                    {item.uuid}
                                </Mono>
                                <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 4, flexWrap: "wrap" }}>
                                    <span className={`konia-chip konia-badge-${tipo.toLowerCase() === "pue" ? "pue" : "ppd"}`}>{tipo}</span>
                                    {sinRep && <span className="konia-chip konia-badge-nr">SIN REP</span>}
                                    {item.rfc && (
                                        <span style={{
                                            fontFamily: "'JetBrains Mono', monospace", fontSize: 10,
                                            fontWeight: 700, color: "#5b6af0",
                                            background: "#5b6af010", padding: "2px 7px",
                                            borderRadius: 5, letterSpacing: "0.03em"
                                        }}>{item.rfc}</span>
                                    )}
                                    {item.nombre && (
                                        <span style={{
                                            fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 10,
                                            fontWeight: 500, color: "#334155",
                                            background: "#f1f5f9", padding: "2px 7px",
                                            borderRadius: 5, maxWidth: 220,
                                            overflow: "hidden", textOverflow: "ellipsis",
                                            whiteSpace: "nowrap"
                                        }} title={item.nombre}>{item.nombre}</span>
                                    )}
                                </div>
                                <div style={{ height: 3, background: "rgba(249,115,22,.1)", borderRadius: 2, overflow: "hidden", width: "80%" }}>
                                    <div style={{
                                        width: `${barW}%`, height: "100%", background: "#f97316", borderRadius: 2,
                                        animation: `barIn .6s ease ${.1 + i * .04}s both`, transformOrigin: "left"
                                    }} />
                                </div>
                            </div>
                            <Mono size={13} color="#f43f5e" weight={700}>{fmtFull(item.monto)}</Mono>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

/* ══════════════════════════════════════════════════════════════════
   SKELETON LOADER
══════════════════════════════════════════════════════════════════ */
const SkeletonKPIs = () => (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, padding: "20px 0" }}>
        {[260, 240, 200].map((h, i) => (
            <div key={i} style={{
                height: h, borderRadius: 18, background: "linear-gradient(90deg,#f1f5f9,#e2e8f0,#f1f5f9)",
                backgroundSize: "200% 100%", animation: "shimmer 1.5s infinite"
            }} />
        ))}
        <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
    </div>
);

/* ══════════════════════════════════════════════════════════════════
   KPIsTab — COMPONENTE PRINCIPAL CON API REAL
══════════════════════════════════════════════════════════════════ */
const KPIsTab = () => {
    const { filters } = useFilterStore();
    const periodoActivo = `${filters.year}-${String(filters.month).padStart(2, "0")}`;
    const [modo, setModo] = useState("cliente");
    const [data, setData] = useState(null);
    const [historico, setHistorico] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!periodoActivo) return;
        setLoading(true);
        setData(null);

        const params = new URLSearchParams({ periodo: periodoActivo });
        if (filters.tipo && filters.tipo.length > 0) params.append("tipo", filters.tipo.join(","));
        if (filters.metodo && filters.metodo.length > 0) params.append("metodo", filters.metodo.join(","));
        if (filters.monto_min !== undefined && filters.monto_min !== null) params.append("monto_min", filters.monto_min);
        if (filters.monto_max !== undefined && filters.monto_max !== null) params.append("monto_max", filters.monto_max);

        api.get(`/api/kpis/resumen?${params.toString()}`)
            .then(res => {
                const d = res.data;
                setData(d);
                if (d.evolucion && Array.isArray(d.evolucion)) {
                    HISTORICO_DATA = d.evolucion;
                    setHistorico(d.evolucion);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [periodoActivo, filters.tipo, filters.metodo, filters.monto_min, filters.monto_max]);

    // Map API response into the shape our components expect
    const mappedData = data ? {
        // Contadores
        totalCFDIs_cliente: data.bloque1_cartera?.total_uuids ?? data.total_uuids ?? 0,
        totalCFDIs_proveedor: data.bloque2_eficiencia?.total_uuids ?? data.total_uuids ?? 0,
        montoTotal_cliente: data.bloque4_inteligencia?.dist_flujo?.emitidos_monto ?? data.saldo_total ?? 0,
        montoTotal_proveedor: data.bloque4_inteligencia?.dist_flujo?.recibidos_monto ?? data.saldo_total ?? 0,
        saldoNeto: data.saldo_total ?? 0,

        // Cartera
        dsoDias: data.bloque1_cartera?.dso ?? 0,
        sinREP_count: data.bloque1_cartera?.sin_rep_count ?? 0,
        sinREP_monto: data.bloque1_cartera?.sin_rep_monto ?? 0,
        recuperacion_pct: data.bloque1_cartera?.recuperacion_pct ?? 0,
        aging: data.bloque1_cartera?.aging?.map(a => ({
            rango: a.rango,
            uuids: a.uuids,
            pct: a.pct,
            color: a.rango === "0-30 días" ? "#10b981" : a.rango === "31-60 días" ? "#f59e0b" : a.rango === "61-90 días" ? "#f97316" : "#f43f5e"
        })) ?? [],

        // Eficiencia
        ncExcesivas: data.bloque2_eficiencia?.nc_excesivas ?? 0,
        ratioNC: data.bloque2_eficiencia?.ratio_nc ?? 0,
        anticipos_n: data.bloque2_eficiencia?.anticipos_n ?? 0,
        anticipos_m: data.bloque2_eficiencia?.anticipos_monto ?? 0,
        otrosSinClass: data.bloque2_eficiencia?.otros_sin_class ?? 0,
        otrosMonto: data.bloque2_eficiencia?.otros_monto ?? 0,

        // Riesgo SAT
        concentracion_pct: data.bloque3_riesgo?.concentracion_pct ?? 0,
        indiceConcentracion: data.bloque3_riesgo?.indice_concentracion ?? 0,

        // KPIs adicionales — ahora todos vienen del backend
        tasaCancelacion: data.tasa_cancelacion ?? 0,
        cfdisCancelados: data.cfdi_cancelados ?? 0,
        eficienciaRecup: data.eficiencia_recuperacion ?? 0,
        diasProxVencer: data.dias_prox_vencer ?? 0,
        // saldo_total positivo = más EMITIDO que recibido = saldo a FAVOR del contribuyente
        posicionFiscal: (data.saldo_total ?? 0) >= 0 ? "FAVOR" : "CARGO",
        deducibilidad_pct: data.deducibilidad_pct ?? 0,
        discrepancia_pct: data.discrepancia_pct ?? 0,

        // Distribución
        emitidos_pct: data.bloque4_inteligencia?.dist_flujo?.emitidos_pct ?? 30,
        recibidos_pct: data.bloque4_inteligencia?.dist_flujo?.recibidos_pct ?? 70,
        emitidos_n: data.bloque4_inteligencia?.dist_flujo?.emitidos_n ?? 0,
        recibidos_n: data.bloque4_inteligencia?.dist_flujo?.recibidos_n ?? 0,
        emitidos_m: data.bloque4_inteligencia?.dist_flujo?.emitidos_monto ?? 0,
        recibidos_m: data.bloque4_inteligencia?.dist_flujo?.recibidos_monto ?? 0,
        cadenas: data.bloque4_inteligencia?.cadenas_largas ?? [],

        // Top 10
        top10: data.top10_negativos ?? [],
    } : null;

    return (
        <div style={{ minHeight: "100vh", background: "#f4f6fb", fontFamily: "'Plus Jakarta Sans',sans-serif", padding: "0 0 48px" }}>
            <style>{CSS}</style>

            {/* Encabezado período */}
            <div className="konia-card" style={{
                padding: "14px 24px",
                borderLeft: "4px solid #5b6af0",
                marginBottom: 4
            }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ width: 4, height: 28, background: "linear-gradient(180deg,#5b6af0,#7c3aed)", borderRadius: 2 }} />
                        <div>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <span style={{ fontSize: 10, fontWeight: 800, color: "#94a3b8", letterSpacing: ".1em" }}>PERÍODO FISCAL:</span>
                                <Mono size={16} color="#5b6af0" weight={700}>{periodoActivo}</Mono>
                            </div>
                            <p style={{ fontSize: 10, color: "#94a3b8", marginTop: 1 }}>Sistema KONIA · Análisis Fiscal CFDI</p>
                        </div>
                    </div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", background: "#10b981", animation: "pulseGreen 1.5s ease infinite" }} />
                        <span style={{ fontSize: 11, color: "#10b981", fontWeight: 700 }}>
                            {loading ? "Cargando..." : "Datos actualizados"}
                        </span>
                    </div>
                </div>
            </div>

            {/* Contenido */}
            <div style={{ padding: "20px 28px", display: "flex", flexDirection: "column", gap: 16, maxWidth: 1400 }}>
                {loading ? (
                    <SkeletonKPIs />
                ) : mappedData ? (
                    <>
                        <KPISuperiores modo={modo} setModo={setModo} data={mappedData} />
                        {historico.length > 0 && <BoxPlotHistorico historico={historico} />}
                        {historico.length > 0 && <GraficaHistorico historico={historico} />}
                        <SaludEficiencia data={mappedData} />
                        <RiesgoDistribucion data={mappedData} />
                        <Top10 data={mappedData} />
                    </>
                ) : (
                    <div style={{ height: 300, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>
                        No hay datos disponibles para el período seleccionado
                    </div>
                )}
            </div>
        </div>
    );
};

export default KPIsTab;
