import {
    LineChart, Line, BarChart, Bar, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, Cell, PieChart, Pie
} from "recharts";
import { useParams, useLocation } from "react-router-dom";
import useUIStore from "../../stores/useUIStore";
import { useEffect, useState, useMemo } from "react";

// ─── FUENTES ────────────────────────────────────────────────────────────────
const fontStyle = `
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700;800&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Montserrat', sans-serif; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes floatA {
    0%,100% { transform: translateY(0px) rotate(0deg); }
    50%      { transform: translateY(-12px) rotate(2deg); }
  }
  @keyframes floatB {
    0%,100% { transform: translateY(0px) rotate(0deg); }
    50%      { transform: translateY(-8px) rotate(-2deg); }
  }
  @keyframes pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.5; }
  }
  @keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  @keyframes barGrow {
    from { transform: scaleX(0); }
    to   { transform: scaleX(1); }
  }
  @keyframes countUp {
    from { opacity: 0; transform: scale(0.8); }
    to   { opacity: 1; transform: scale(1); }
  }

  .card-hover {
    transition: transform 0.25s ease, box-shadow 0.25s ease;
  }
  .card-hover:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
  }
  .tab-btn {
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    outline: none;
  }
  .rfc-row {
    transition: background 0.15s ease;
  }
  .rfc-row:hover {
    background: rgba(107,132,243,0.06) !important;
  }
  .period-pill {
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    outline: none;
  }
  .period-pill:hover {
    transform: translateY(-1px);
  }
`;

// ─── DATOS MOCK ─────────────────────────────────────────────────────────────
const PERIODOS = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02"];

const LABELS = {
    "2025-10": "Oct 25", "2025-11": "Nov 25", "2025-12": "Dic 25",
    "2026-01": "Ene 26", "2026-02": "Feb 26"
};

const TENDENCIAS = [
    {
        periodo: "Oct 25", ppd: 4200000, pue: 2800000, otros: 320000,
        tasa_rec: 61, sin_rep: 180, dso: 38
    },
    {
        periodo: "Nov 25", ppd: 3900000, pue: 3100000, otros: 280000,
        tasa_rec: 65, sin_rep: 155, dso: 34
    },
    {
        periodo: "Dic 25", ppd: 5100000, pue: 2600000, otros: 410000,
        tasa_rec: 58, sin_rep: 210, dso: 42
    },
    {
        periodo: "Ene 26", ppd: 4600000, pue: 3300000, otros: 290000,
        tasa_rec: 70, sin_rep: 142, dso: 31
    },
    {
        periodo: "Feb 26", ppd: 4400000, pue: 3000000, otros: 310000,
        tasa_rec: 69, sin_rep: 142, dso: 29
    },
];

const RFCS_CLIENTES = [
    {
        rfc: "PME380607P35", nombre: "PETRÓLEOS MEXICANOS",
        monto: 2294934, periodos: 5, nc_pct: 0.8
    },
    {
        rfc: "SGD101111JP1", nombre: "SUPER DE GDL",
        monto: 935299, periodos: 5, nc_pct: 1.2
    },
    {
        rfc: "DHL500226BX4", nombre: "DHL EXPRESS MÉXICO",
        monto: 742180, periodos: 4, nc_pct: 0.3
    },
    {
        rfc: "OCA711115TP8", nombre: "OCAMPO CARGAS",
        monto: 621400, periodos: 3, nc_pct: 2.1
    },
    {
        rfc: "TFR920301AB3", nombre: "TRANSPORTES FRESA",
        monto: 498200, periodos: 5, nc_pct: 0.5
    },
    {
        rfc: "GDE810422KL9", nombre: "GRUPO DE ENERGÍA",
        monto: 382900, periodos: 2, nc_pct: 4.8
    },
    {
        rfc: "LSO130618R5", nombre: "LOGÍSTICA SONDA",
        monto: 294100, periodos: 4, nc_pct: 1.1
    },
    {
        rfc: "MXC970814UV2", nombre: "MEXICALCO SA",
        monto: 201340, periodos: 3, nc_pct: 0.9
    },
];

const RFCS_PROVEEDORES = [
    {
        rfc: "CSO1304138Z0", nombre: "CONROE SOLUCIONES",
        ppd_sin_rep: 82, monto: 962781, aging: "+90d"
    },
    {
        rfc: "GPE190327DT7", nombre: "GRUPO PECARE",
        ppd_sin_rep: 24, monto: 341200, aging: "31-60d"
    },
    {
        rfc: "ABC980201XY3", nombre: "ABARROTES CENTRO",
        ppd_sin_rep: 18, monto: 218400, aging: "61-90d"
    },
    {
        rfc: "TEC011203QP7", nombre: "TECNOGAS SA",
        ppd_sin_rep: 11, monto: 142800, aging: "31-60d"
    },
    {
        rfc: "FLU230415MM1", nombre: "FLUIDOS MONTERREY",
        ppd_sin_rep: 6, monto: 89300, aging: "0-30d"
    },
];

const AGING_HIST = [
    { periodo: "Oct 25", d30: 45, d60: 28, d90: 18, mas90: 9 },
    { periodo: "Nov 25", d30: 48, d60: 26, d90: 16, mas90: 10 },
    { periodo: "Dic 25", d30: 38, d60: 30, d90: 20, mas90: 12 },
    { periodo: "Ene 26", d30: 52, d60: 28, d90: 12, mas90: 8 },
    { periodo: "Feb 26", d30: 55, d60: 27, d90: 11, mas90: 7 },
];

const PATRONES_DIA = [
    { dia: "Lun", cfdi: 1820 }, { dia: "Mar", cfdi: 2340 },
    { dia: "Mié", cfdi: 2180 }, { dia: "Jue", cfdi: 2490 },
    { dia: "Vie", cfdi: 2820 }, { dia: "Sáb", cfdi: 420 },
    { dia: "Dom", cfdi: 180 },
];

const OTROS_HIST = [
    { periodo: "Oct 25", pct: 8.2 }, { periodo: "Nov 25", pct: 7.8 },
    { periodo: "Dic 25", pct: 9.4 }, { periodo: "Ene 26", pct: 7.1 },
    { periodo: "Feb 26", pct: 6.9 },
];

const RADAR_DATA = [
    { metric: "Recuperación PPD", value: 69 },
    { metric: "Diversif. RFC", value: 98 },
    { metric: "Clasif. Segmento", value: 93 },
    { metric: "Cobertura REP", value: 69 },
    { metric: "Antigüedad Saldo", value: 82 },
    { metric: "Volumen Documental", value: 88 },
];

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const fmt = (n, compact = false) => {
    if (n == null) return "$0";
    if (compact) {
        if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
        if (Math.abs(n) >= 1e3) return `$${(n / 1e3).toFixed(0)}K`;
    }
    return new Intl.NumberFormat("es-MX", {
        style: "currency", currency: "MXN", minimumFractionDigits: 0
    }).format(n);
};

const COLORS = {
    blue: "#6B84F3",
    purple: "#785799",
    green: "#26A69A",
    amber: "#FFCA28",
    coral: "#FF8A65",
    red: "#ef4444",
    cyan: "#00BCD4",
    slate: "#94a3b8",
};

// ─── CUSTOM TOOLTIP ───────────────────────────────────────────────────────────
const KTooltip = ({ active, payload, label, prefix = "" }) => {
    if (!active || !payload?.length) return null;
    return (
        <div style={{
            background: "rgba(255,255,255,0.95)",
            border: "1px solid rgba(107,132,243,0.3)",
            borderRadius: "12px", padding: "10px 14px",
            backdropFilter: "blur(8px)"
        }}>
            <p style={{
                fontSize: "10px", fontFamily: "Montserrat",
                fontWeight: 700, color: "#64748b",
                letterSpacing: "0.08em", textTransform: "uppercase",
                marginBottom: "6px"
            }}>{label}</p>
            {payload.map((p, i) => (
                <div key={i} style={{
                    display: "flex", gap: "8px",
                    alignItems: "center", marginBottom: "2px"
                }}>
                    <div style={{
                        width: "8px", height: "8px",
                        borderRadius: "50%", background: p.color,
                        flexShrink: 0
                    }} />
                    <span style={{
                        fontSize: "12px", fontFamily: "JetBrains Mono",
                        fontWeight: 700, color: "#1e293b"
                    }}>
                        {prefix}{typeof p.value === "number" && p.value > 1000
                            ? fmt(p.value, true) : p.value}
                    </span>
                    <span style={{
                        fontSize: "10px", fontFamily: "Montserrat",
                        color: "#64748b"
                    }}>{p.name}</span>
                </div>
            ))}
        </div>
    );
};

// ─── METRIC CARD ─────────────────────────────────────────────────────────────
const MetricCard = ({ label, value, sub, color, delay = 0, icon }) => (
    <div className="card-hover" style={{
        background: "#ffffff",
        borderRadius: "16px", padding: "20px 24px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
        borderTop: `3px solid ${color}`,
        animation: `fadeUp 0.5s ease ${delay}s both`,
        position: "relative", overflow: "hidden"
    }}>
        <div style={{
            position: "absolute", top: "-20px", right: "-20px",
            width: "80px", height: "80px", borderRadius: "50%",
            background: `${color}08`
        }} />
        <p style={{
            fontSize: "10px", fontFamily: "Montserrat",
            fontWeight: 700, color: COLORS.slate,
            letterSpacing: "0.08em", textTransform: "uppercase",
            marginBottom: "8px"
        }}>{label}</p>
        <p style={{
            fontSize: "28px", fontFamily: "JetBrains Mono",
            fontWeight: 800, color, lineHeight: 1,
            animation: `countUp 0.6s ease ${delay + 0.1}s both`
        }}>{value}</p>
        {sub && <p style={{
            fontSize: "11px", fontFamily: "Montserrat",
            color: "#64748b", marginTop: "6px"
        }}>{sub}</p>}
    </div>
);

// ─── SECTION HEADER ──────────────────────────────────────────────────────────
const SectionHeader = ({ title, sub, color, delay = 0 }) => (
    <div style={{
        display: "flex", flexDirection: "column", gap: "4px",
        marginBottom: "20px",
        animation: `fadeUp 0.5s ease ${delay}s both`
    }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{
                width: "4px", height: "16px", borderRadius: "2px",
                background: color, display: "inline-block"
            }} />
            <p style={{
                fontSize: "11px", fontFamily: "JetBrains Mono",
                fontWeight: 700, color: "#94a3b8",
                letterSpacing: "0.1em", textTransform: "uppercase"
            }}>{title}</p>
        </div>
        {sub && <p style={{
            fontSize: "11px", fontFamily: "Montserrat",
            color: "#64748b", marginLeft: "12px", marginTop: "1px"
        }}>{sub}</p>}
    </div>
);

// ─── BLOQUE 1: TENDENCIAS HISTÓRICAS ─────────────────────────────────────────
const BloqueTendencias = () => {
    const pred_ppd = Math.round((TENDENCIAS[3].ppd + TENDENCIAS[4].ppd) / 2);
    const pred_pue = Math.round((TENDENCIAS[3].pue + TENDENCIAS[4].pue) / 2);
    const crecPPD = ((TENDENCIAS[4].ppd - TENDENCIAS[0].ppd) / TENDENCIAS[0].ppd * 100).toFixed(1);
    const tendDSO = TENDENCIAS[4].dso - TENDENCIAS[0].dso;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* KPIs rápidos */}
            <div style={{
                display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "12px",
                animation: "fadeUp 0.4s ease both"
            }}>
                {[
                    {
                        label: "Crecimiento PPD", value: `${crecPPD > 0 ? "+" : ""}${crecPPD}%`,
                        sub: "Oct 25 → Feb 26", color: crecPPD > 0 ? COLORS.green : COLORS.coral
                    },
                    {
                        label: "Vol. Feb 26", value: fmt(TENDENCIAS[4].ppd + TENDENCIAS[4].pue, true),
                        sub: "PPD + PUE total", color: COLORS.blue
                    },
                    {
                        label: "DSO Tendencia", value: `${tendDSO > 0 ? "+" : ""}${tendDSO}d`,
                        sub: "variación días cobro",
                        color: tendDSO < 0 ? COLORS.green : COLORS.coral
                    },
                    {
                        label: "Predicción Mar 26", value: fmt(pred_ppd + pred_pue, true),
                        sub: "promedio móvil", color: COLORS.amber
                    },
                ].map((m, i) => (
                    <MetricCard key={i} {...m} delay={i * 0.08} />
                ))}
            </div>

            {/* Gráfica evolución PPD vs PUE */}
            <div className="card-hover" style={{
                background: "#ffffff",
                borderRadius: "16px", padding: "24px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                borderTop: `3px solid ${COLORS.blue}`,
                animation: "fadeUp 0.5s ease 0.2s both"
            }}>
                <SectionHeader
                    title="Evolución Facturación PPD vs PUE"
                    sub="Monto total por período — 5 meses"
                    color={COLORS.blue} delay={0.3}
                />
                <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={TENDENCIAS}>
                        <defs>
                            <linearGradient id="gPPD" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="gPUE" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
                        <XAxis dataKey="periodo" tick={{
                            fontSize: 10, fontFamily: "Montserrat",
                            fill: "#64748b", fontWeight: 600
                        }} axisLine={false} tickLine={false} />
                        <YAxis tickFormatter={v => fmt(v, true)} tick={{
                            fontSize: 10, fontFamily: "JetBrains Mono", fill: "#64748b"
                        }} axisLine={false} tickLine={false} />
                        <Tooltip content={<KTooltip prefix="" />} />
                        <Area type="monotone" dataKey="ppd" name="PPD"
                            stroke={COLORS.purple} fill="url(#gPPD)"
                            strokeWidth={2.5} dot={{ fill: COLORS.purple, r: 3 }} />
                        <Area type="monotone" dataKey="pue" name="PUE"
                            stroke={COLORS.blue} fill="url(#gPUE)"
                            strokeWidth={2.5} dot={{ fill: COLORS.blue, r: 3 }} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Fila inferior: tasa recuperación + DSO */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="card-hover" style={{
                    background: "#ffffff",
                    borderRadius: "16px", padding: "24px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                    borderTop: `3px solid ${COLORS.green}`,
                    animation: "fadeUp 0.5s ease 0.35s both"
                }}>
                    <SectionHeader
                        title="Tasa de Recuperación PPD"
                        sub="% con complemento de pago"
                        color={COLORS.green} delay={0.4}
                    />
                    <ResponsiveContainer width="100%" height={140}>
                        <LineChart data={TENDENCIAS}>
                            <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
                            <XAxis dataKey="periodo" tick={{
                                fontSize: 9,
                                fontFamily: "Montserrat", fill: "#64748b"
                            }}
                                axisLine={false} tickLine={false} />
                            <YAxis domain={[50, 80]} tickFormatter={v => `${v}%`}
                                tick={{
                                    fontSize: 9, fontFamily: "JetBrains Mono",
                                    fill: "#64748b"
                                }} axisLine={false} tickLine={false} />
                            <Tooltip content={<KTooltip />} />
                            <Line type="monotone" dataKey="tasa_rec" name="Recuperación %"
                                stroke={COLORS.green} strokeWidth={2.5}
                                dot={{
                                    fill: COLORS.green, r: 4, strokeWidth: 2,
                                    stroke: "rgba(38,166,154,0.3)"
                                }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="card-hover" style={{
                    background: "#ffffff",
                    borderRadius: "16px", padding: "24px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                    borderTop: `3px solid ${COLORS.amber}`,
                    animation: "fadeUp 0.5s ease 0.4s both"
                }}>
                    <SectionHeader
                        title="DSO — Días de Cobro"
                        sub="Promedio días factura → pago"
                        color={COLORS.amber} delay={0.45}
                    />
                    <ResponsiveContainer width="100%" height={140}>
                        <BarChart data={TENDENCIAS}>
                            <CartesianGrid stroke="#e2e8f0"
                                strokeDasharray="4 4" />
                            <XAxis dataKey="periodo" tick={{
                                fontSize: 9,
                                fontFamily: "Montserrat", fill: "#64748b"
                            }}
                                axisLine={false} tickLine={false} />
                            <YAxis tick={{
                                fontSize: 9, fontFamily: "JetBrains Mono",
                                fill: "#64748b"
                            }} axisLine={false} tickLine={false} />
                            <Tooltip content={<KTooltip />} />
                            <Bar dataKey="dso" name="Días" radius={[4, 4, 0, 0]}>
                                {TENDENCIAS.map((_, i) => (
                                    <Cell key={i} fill={
                                        TENDENCIAS[i].dso > 40 ? COLORS.coral :
                                            TENDENCIAS[i].dso > 30 ? COLORS.amber : COLORS.green
                                    } />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

// ─── BLOQUE 2: ANÁLISIS DE RFCs ──────────────────────────────────────────────
const BloqueRFCs = () => {
    const [vista, setVista] = useState("clientes");
    const maxMonto = Math.max(...RFCS_CLIENTES.map(r => r.monto));

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Toggle */}
            <div style={{
                display: "flex", gap: "8px",
                animation: "fadeUp 0.4s ease both"
            }}>
                {[
                    { key: "clientes", label: "Top Clientes RFC", color: COLORS.blue },
                    { key: "proveedores", label: "Proveedores en Riesgo", color: COLORS.coral },
                ].map(t => (
                    <button key={t.key} className="tab-btn"
                        onClick={() => setVista(t.key)}
                        style={{
                            padding: "8px 20px", borderRadius: "20px",
                            fontSize: "11px", fontFamily: "Montserrat",
                            fontWeight: 700,
                            background: vista === t.key
                                ? `linear-gradient(135deg, ${t.color}30, ${t.color}15)`
                                : "#f1f5f9",
                            color: vista === t.key ? t.color : "#64748b",
                            border: vista === t.key
                                ? `1px solid ${t.color}40`
                                : "1px solid #e2e8f0",
                        }}>
                        {t.label}
                    </button>
                ))}
            </div>

            {vista === "clientes" ? (
                <div className="card-hover" style={{
                    background: "#ffffff",
                    borderRadius: "16px", padding: "24px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                    borderTop: `3px solid ${COLORS.blue}`,
                    animation: "fadeUp 0.4s ease both"
                }}>
                    <SectionHeader
                        title="Top Clientes por Volumen Histórico"
                        sub="Suma de saldo acumulado todos los períodos"
                        color={COLORS.blue}
                    />
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {RFCS_CLIENTES.map((r, i) => {
                            const pct = (r.monto / maxMonto * 100).toFixed(0);
                            return (
                                <div key={i} className="rfc-row" style={{
                                    padding: "12px 14px", borderRadius: "12px",
                                    background: "transparent"
                                }}>
                                    <div style={{
                                        display: "flex", justifyContent: "space-between",
                                        alignItems: "flex-start", marginBottom: "6px"
                                    }}>
                                        <div style={{
                                            display: "flex", gap: "10px",
                                            alignItems: "center"
                                        }}>
                                            <span style={{
                                                width: "22px", height: "22px",
                                                borderRadius: "8px",
                                                background: i < 3
                                                    ? `${COLORS.blue}20` : "rgba(255,255,255,0.05)",
                                                display: "flex", alignItems: "center",
                                                justifyContent: "center",
                                                fontSize: "10px", fontFamily: "Montserrat",
                                                fontWeight: 800,
                                                color: i < 3 ? COLORS.blue : "#64748b"
                                            }}>{i + 1}</span>
                                            <div>
                                                <p style={{
                                                    fontSize: "12px",
                                                    fontFamily: "Montserrat", fontWeight: 700,
                                                    color: "#1e293b"
                                                }}>{r.nombre}</p>
                                                <p style={{
                                                    fontSize: "10px",
                                                    fontFamily: "JetBrains Mono", color: "#64748b",
                                                    marginTop: "1px"
                                                }}>{r.rfc}</p>
                                            </div>
                                        </div>
                                        <div style={{ textAlign: "right" }}>
                                            <p style={{
                                                fontSize: "14px",
                                                fontFamily: "JetBrains Mono", fontWeight: 800,
                                                color: COLORS.blue
                                            }}>{fmt(r.monto, true)}</p>
                                            <div style={{
                                                display: "flex", gap: "6px",
                                                justifyContent: "flex-end",
                                                marginTop: "3px"
                                            }}>
                                                <span style={{
                                                    fontSize: "9px", fontFamily: "Montserrat",
                                                    fontWeight: 700,
                                                    color: r.nc_pct > 3 ? COLORS.coral :
                                                        r.nc_pct > 1.5 ? COLORS.amber : COLORS.green,
                                                    background: r.nc_pct > 3 ? `${COLORS.coral}15` :
                                                        r.nc_pct > 1.5 ? `${COLORS.amber}15` :
                                                            `${COLORS.green}15`,
                                                    padding: "1px 6px", borderRadius: "4px"
                                                }}>NC {r.nc_pct}%</span>
                                                <span style={{
                                                    fontSize: "9px", fontFamily: "Montserrat",
                                                    fontWeight: 700, color: "#64748b",
                                                    background: "#f1f5f9",
                                                    padding: "1px 6px", borderRadius: "4px"
                                                }}>{r.periodos}p</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{
                                        height: "4px", background: "#f1f5f9",
                                        borderRadius: "2px", overflow: "hidden"
                                    }}>
                                        <div style={{
                                            width: `${pct}%`, height: "100%",
                                            background: `linear-gradient(90deg, ${COLORS.blue}, ${COLORS.purple})`,
                                            borderRadius: "2px",
                                            animation: `barGrow 0.8s ease ${i * 0.06}s both`,
                                            transformOrigin: "left"
                                        }} />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ) : (
                <div className="card-hover" style={{
                    background: "#ffffff",
                    borderRadius: "16px", padding: "24px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                    borderTop: `3px solid ${COLORS.coral}`,
                    animation: "fadeUp 0.4s ease both"
                }}>
                    <SectionHeader
                        title="Proveedores con PPD Sin REP"
                        sub="Mayor riesgo de IVA no acreditable"
                        color={COLORS.coral}
                    />
                    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                        {RFCS_PROVEEDORES.map((r, i) => {
                            const agingColor = {
                                "+90d": "#ef4444", "61-90d": COLORS.coral,
                                "31-60d": COLORS.amber, "0-30d": COLORS.green
                            }[r.aging];
                            return (
                                <div key={i} className="rfc-row" style={{
                                    display: "flex", justifyContent: "space-between",
                                    alignItems: "center", padding: "14px 16px",
                                    borderRadius: "14px",
                                    background: "#ffffff",
                                    border: "1px solid rgba(255,255,255,0.05)"
                                }}>
                                    <div>
                                        <p style={{
                                            fontSize: "12px",
                                            fontFamily: "Montserrat", fontWeight: 700,
                                            color: "#1e293b"
                                        }}>{r.nombre}</p>
                                        <p style={{
                                            fontSize: "10px",
                                            fontFamily: "JetBrains Mono", color: "#64748b",
                                            marginTop: "2px"
                                        }}>{r.rfc}</p>
                                    </div>
                                    <div style={{
                                        display: "flex", gap: "10px",
                                        alignItems: "center"
                                    }}>
                                        <div style={{ textAlign: "right" }}>
                                            <p style={{
                                                fontSize: "13px",
                                                fontFamily: "JetBrains Mono", fontWeight: 800,
                                                color: COLORS.coral
                                            }}>{fmt(r.monto, true)}</p>
                                            <p style={{
                                                fontSize: "10px",
                                                fontFamily: "Montserrat", color: "#64748b",
                                                marginTop: "1px"
                                            }}>{r.ppd_sin_rep} UUIDs sin REP</p>
                                        </div>
                                        <span style={{
                                            fontSize: "10px", fontFamily: "Montserrat",
                                            fontWeight: 700, color: agingColor,
                                            background: `${agingColor}15`,
                                            border: `1px solid ${agingColor}30`,
                                            padding: "4px 10px", borderRadius: "20px",
                                            flexShrink: 0
                                        }}>{r.aging}</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

// ─── BLOQUE 3: RIESGO DE CARTERA ─────────────────────────────────────────────
const BloqueCartera = () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr", gap: "16px"
        }}>
            {/* Aging histórico */}
            <div className="card-hover" style={{
                background: "#ffffff",
                borderRadius: "16px", padding: "24px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                borderTop: `3px solid ${COLORS.purple}`,
                animation: "fadeUp 0.4s ease both"
            }}>
                <SectionHeader
                    title="Aging PPD Histórico"
                    sub="Distribución % por antigüedad"
                    color={COLORS.purple} delay={0.4}
                />
                <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={AGING_HIST} barCategoryGap="30%">
                        <CartesianGrid stroke="#e2e8f0"
                            strokeDasharray="4 4" />
                        <XAxis dataKey="periodo" tick={{
                            fontSize: 9,
                            fontFamily: "Montserrat", fill: "#64748b"
                        }}
                            axisLine={false} tickLine={false} />
                        <YAxis tickFormatter={v => `${v}%`} tick={{
                            fontSize: 9,
                            fontFamily: "JetBrains Mono", fill: "#64748b"
                        }}
                            axisLine={false} tickLine={false} />
                        <Tooltip content={<KTooltip />} />
                        <Bar dataKey="d30" name="0-30d" stackId="a"
                            fill={COLORS.green} radius={[0, 0, 0, 0]} />
                        <Bar dataKey="d60" name="31-60d" stackId="a"
                            fill={COLORS.amber} />
                        <Bar dataKey="d90" name="61-90d" stackId="a"
                            fill={COLORS.coral} />
                        <Bar dataKey="mas90" name="+90d" stackId="a"
                            fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
                {/* Leyenda */}
                <div style={{
                    display: "flex", gap: "12px",
                    flexWrap: "wrap", marginTop: "10px"
                }}>
                    {[
                        [COLORS.green, "0-30d"], [COLORS.amber, "31-60d"],
                        [COLORS.coral, "61-90d"], ["#ef4444", "+90d"]
                    ].map(([c, l], i) => (
                        <div key={i} style={{
                            display: "flex", gap: "5px", alignItems: "center"
                        }}>
                            <div style={{
                                width: "8px", height: "8px",
                                borderRadius: "2px", background: c
                            }} />
                            <span style={{
                                fontSize: "9px", fontFamily: "Montserrat",
                                fontWeight: 600, color: "#64748b"
                            }}>{l}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Radar de salud */}
            <div className="card-hover" style={{
                background: "#ffffff",
                borderRadius: "16px", padding: "24px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                borderTop: `3px solid ${COLORS.cyan}`,
                animation: "fadeUp 0.4s ease 0.15s both"
            }}>
                <SectionHeader
                    title="Índice de Salud Fiscal"
                    sub="Puntuación multidimensional Feb 26"
                    color={COLORS.cyan} delay={0.15}
                />
                <ResponsiveContainer width="100%" height={200}>
                    <RadarChart data={RADAR_DATA}>
                        <PolarGrid stroke="rgba(255,255,255,0.08)" />
                        <PolarAngleAxis dataKey="metric" tick={{
                            fontSize: 8, fontFamily: "Montserrat",
                            fill: "#64748b", fontWeight: 600
                        }} />
                        <Radar dataKey="value" name="Score"
                            stroke={COLORS.cyan} fill={COLORS.cyan}
                            fillOpacity={0.15} strokeWidth={2} />
                    </RadarChart>
                </ResponsiveContainer>
            </div>
        </div>

        {/* Saldo insoluto acumulado */}
        <div className="card-hover" style={{
            background: "#ffffff",
            borderRadius: "16px", padding: "24px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
            borderTop: `3px solid ${COLORS.coral}`,
            animation: "fadeUp 0.5s ease 0.25s both"
        }}>
            <SectionHeader
                title="Saldo Insoluto PPD — Evolución"
                sub="UUIDs sin REP: montos pendientes acumulados por período"
                color={COLORS.coral} delay={0.25}
            />
            <ResponsiveContainer width="100%" height={160}>
                <AreaChart data={[
                    { periodo: "Oct 25", sin_rep: 180, monto: 1420000 },
                    { periodo: "Nov 25", sin_rep: 155, monto: 1180000 },
                    { periodo: "Dic 25", sin_rep: 210, monto: 1650000 },
                    { periodo: "Ene 26", sin_rep: 142, monto: 1020000 },
                    { periodo: "Feb 26", sin_rep: 142, monto: 962781 },
                ]}>
                    <defs>
                        <linearGradient id="gCoral" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.coral} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={COLORS.coral} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#e2e8f0"
                        strokeDasharray="4 4" />
                    <XAxis dataKey="periodo" tick={{
                        fontSize: 9,
                        fontFamily: "Montserrat", fill: "#64748b"
                    }}
                        axisLine={false} tickLine={false} />
                    <YAxis tickFormatter={v => fmt(v, true)} tick={{
                        fontSize: 9,
                        fontFamily: "JetBrains Mono", fill: "#64748b"
                    }}
                        axisLine={false} tickLine={false} />
                    <Tooltip content={<KTooltip />} />
                    <Area type="monotone" dataKey="monto" name="Monto sin REP"
                        stroke={COLORS.coral} fill="url(#gCoral)"
                        strokeWidth={2.5}
                        dot={{ fill: COLORS.coral, r: 4 }} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    </div>
);

// ─── BLOQUE 4: PATRONES ───────────────────────────────────────────────────────
const BloquePatrones = () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr", gap: "16px"
        }}>
            {/* Distribución por día de semana */}
            <div className="card-hover" style={{
                background: "#ffffff",
                borderRadius: "16px", padding: "24px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                borderTop: `3px solid ${COLORS.blue}`,
                animation: "fadeUp 0.4s ease both"
            }}>
                <SectionHeader
                    title="Emisión por Día de Semana"
                    sub="Concentración de CFDIs — promedio histórico"
                    color={COLORS.blue} delay={0.4}
                />
                <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={PATRONES_DIA} barCategoryGap="25%">
                        <CartesianGrid stroke="#e2e8f0"
                            strokeDasharray="4 4" />
                        <XAxis dataKey="dia" tick={{
                            fontSize: 10,
                            fontFamily: "Montserrat", fontWeight: 700,
                            fill: "#64748b"
                        }} axisLine={false} tickLine={false} />
                        <YAxis tick={{
                            fontSize: 9, fontFamily: "JetBrains Mono",
                            fill: "#64748b"
                        }} axisLine={false} tickLine={false} />
                        <Tooltip content={<KTooltip />} />
                        <Bar dataKey="cfdi" name="CFDIs" radius={[6, 6, 0, 0]}>
                            {PATRONES_DIA.map((d, i) => (
                                <Cell key={i} fill={
                                    d.cfdi === Math.max(...PATRONES_DIA.map(x => x.cfdi))
                                        ? COLORS.blue
                                        : d.cfdi < 500
                                            ? "rgba(107,132,243,0.2)"
                                            : "rgba(107,132,243,0.5)"
                                } />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Ratio OTROS histórico */}
            <div className="card-hover" style={{
                background: "#ffffff",
                borderRadius: "16px", padding: "24px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
                borderTop: `3px solid ${COLORS.purple}`,
                animation: "fadeUp 0.4s ease 0.12s both"
            }}>
                <SectionHeader
                    title="Ratio OTROS / Total"
                    sub="% de UUIDs sin clasificar — tendencia"
                    color={COLORS.purple} delay={0.12}
                />
                <ResponsiveContainer width="100%" height={150}>
                    <LineChart data={OTROS_HIST}>
                        <CartesianGrid stroke="#e2e8f0"
                            strokeDasharray="4 4" />
                        <XAxis dataKey="periodo" tick={{
                            fontSize: 9,
                            fontFamily: "Montserrat", fill: "#64748b"
                        }}
                            axisLine={false} tickLine={false} />
                        <YAxis tickFormatter={v => `${v}%`} domain={[5, 12]}
                            tick={{
                                fontSize: 9, fontFamily: "JetBrains Mono",
                                fill: "#64748b"
                            }} axisLine={false} tickLine={false} />
                        <Tooltip content={<KTooltip />} />
                        <Line type="monotone" dataKey="pct" name="OTROS %"
                            stroke={COLORS.purple} strokeWidth={2.5}
                            strokeDasharray="5 3"
                            dot={{
                                fill: COLORS.purple, r: 5,
                                stroke: "rgba(120,87,153,0.3)", strokeWidth: 6
                            }} />
                    </LineChart>
                </ResponsiveContainer>
                <div style={{
                    display: "flex", alignItems: "center", gap: "8px",
                    marginTop: "12px", padding: "10px 14px",
                    background: "rgba(255,202,40,0.08)",
                    border: "1px solid rgba(255,202,40,0.2)",
                    borderRadius: "10px"
                }}>
                    <div style={{ width: "20px" }} />
                    <p style={{
                        fontSize: "11px", fontFamily: "Montserrat",
                        fontWeight: 600, color: COLORS.purple
                    }}>
                        Tendencia a la baja — mejora en clasificación
                    </p>
                </div>
            </div>
        </div>

        {/* Monto promedio por UUID */}
        <div className="card-hover" style={{
            background: "#ffffff",
            borderRadius: "16px", padding: "24px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
            borderTop: `3px solid ${COLORS.green}`,
            animation: "fadeUp 0.5s ease 0.2s both"
        }}>
            <SectionHeader
                title="Ticket Promedio por UUID"
                sub="Monto promedio — comparativo PPD vs PUE vs OTROS"
                color={COLORS.green}
            />
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "16px"
            }}>
                {[
                    { periodo: "Oct 25", ppd: 3820, pue: 2100, otros: 890 },
                    { periodo: "Nov 25", ppd: 3640, pue: 2280, otros: 810 },
                    { periodo: "Dic 25", ppd: 4100, pue: 1980, otros: 1020 },
                    { periodo: "Ene 26", ppd: 3750, pue: 2340, otros: 870 },
                    { periodo: "Feb 26", ppd: 3900, pue: 2190, otros: 790 },
                ].map((d, i) => (
                    <div key={i} style={{
                        background: "#ffffff",
                        borderRadius: "14px", padding: "14px",
                        border: "1px solid #e2e8f0"
                    }}>
                        <p style={{
                            fontSize: "9px", fontFamily: "Montserrat",
                            fontWeight: 700, color: "#64748b",
                            letterSpacing: "0.08em",
                            textTransform: "uppercase",
                            marginBottom: "10px"
                        }}>{d.periodo}</p>
                        {[
                            { key: "ppd", label: "PPD", val: d.ppd, color: COLORS.purple },
                            { key: "pue", label: "PUE", val: d.pue, color: COLORS.blue },
                            { key: "otros", label: "OTROS", val: d.otros, color: "#64748b" },
                        ].map((s, j) => (
                            <div key={j} style={{ marginBottom: "6px" }}>
                                <div style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    marginBottom: "2px"
                                }}>
                                    <span style={{
                                        fontSize: "9px",
                                        fontFamily: "Montserrat", fontWeight: 600,
                                        color: s.color
                                    }}>{s.label}</span>
                                    <span style={{
                                        fontSize: "9px",
                                        fontFamily: "JetBrains Mono", fontWeight: 700,
                                        color: s.color
                                    }}>${(s.val / 1000).toFixed(1)}K</span>
                                </div>
                                <div style={{
                                    height: "3px",
                                    background: "#f1f5f9",
                                    borderRadius: "2px", overflow: "hidden"
                                }}>
                                    <div style={{
                                        width: `${s.val / 50}%`, height: "100%",
                                        background: s.color, borderRadius: "2px",
                                        opacity: 0.7
                                    }} />
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    </div>
);

// ─── APP PRINCIPAL ────────────────────────────────────────────────────────────
export default function KoniaAnalitica() {
    const { subtab } = useParams();
    const { setActiveModule } = useUIStore();

    useEffect(() => {
        // Asegurar que el módulo activo sea cuenta-t para mostrar SubTabNav
        setActiveModule('cuenta-t');
    }, [setActiveModule]);

    // Mapeo de subruta a contenido interno
    const currentTab = subtab === "rfc" ? "rfcs" :
        subtab === "cartera" ? "cartera" :
            subtab === "patrones" ? "patrones" :
                "tendencias";

    return (
        <div style={{
            minHeight: "100vh",
            background: "#ffffff",
            fontFamily: "Montserrat, sans-serif",
            position: "relative"
        }}>
            <style>{fontStyle}</style>

            {/* Mesh background */}
            <div style={{
                position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none"
            }}>
                <div style={{
                    position: "absolute", top: "-20%", left: "-10%",
                    width: "50%", height: "50%", borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(107,132,243,0.04) 0%, transparent 70%)",
                    animation: "floatA 8s ease-in-out infinite"
                }} />
                <div style={{
                    position: "absolute", bottom: "-20%", right: "-10%",
                    width: "40%", height: "40%", borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(120,87,153,0.04) 0%, transparent 70%)",
                    animation: "floatB 10s ease-in-out infinite"
                }} />
                <div style={{
                    position: "absolute", top: "40%", right: "20%",
                    width: "30%", height: "30%", borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(38,166,154,0.04) 0%, transparent 70%)",
                    animation: "floatA 12s ease-in-out infinite 2s"
                }} />
            </div>

            {/* El Header / Tabs Nav interno ha sido eliminado para integrarse en el Layout global */}

            {/* Content */}
            <div style={{
                position: "relative", zIndex: 1,
                padding: "0 32px 40px", // Eliminado padding superior ya que Layout+SubTabNav ya proveen estructura
                maxWidth: "1400px"
            }}>
                {currentTab === "tendencias" && <BloqueTendencias />}
                {currentTab === "rfcs" && <BloqueRFCs />}
                {currentTab === "cartera" && <BloqueCartera />}
                {currentTab === "patrones" && <BloquePatrones />}
            </div>
        </div>
    );
}
