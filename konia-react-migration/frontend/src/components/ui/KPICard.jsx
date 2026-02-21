
import React from 'react';

const KPICard = ({ title, value, icon: Icon, accentColor, isLoading }) => {
    if (isLoading) {
        return (
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 h-[90px] animate-pulse flex items-center justify-between">
                <div className="space-y-2">
                    <div className="h-3 w-20 bg-slate-100 rounded"></div>
                    <div className="h-6 w-32 bg-slate-100 rounded"></div>
                </div>
                <div className="h-10 w-10 bg-slate-100 rounded-full"></div>
            </div>
        );
    }

    return (
        <div
            style={{
                background: "white",
                borderRadius: "16px",
                padding: "20px 24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06)",
                position: "relative",
                overflow: "hidden",
                height: "90px",
                transition: "box-shadow 0.2s ease",
            }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.10)"}
            onMouseLeave={e => e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06)"}
        >
            {/* Borde izquierdo vertical centrado */}
            <div style={{
                position: "absolute",
                left: 0,
                top: "20%",
                height: "60%",
                width: "3px",
                background: accentColor,
                borderRadius: "0 3px 3px 0"
            }} />

            {/* Contenido izquierdo */}
            <div style={{ paddingLeft: "8px" }}>
                <p style={{
                    fontSize: "12px", // Increased from 10px
                    fontWeight: "700",
                    letterSpacing: "0.06em", // Updated letterSpacing
                    color: "#94a3b8",
                    textTransform: "uppercase",
                    fontFamily: "Montserrat", // Changed to Montserrat
                    marginBottom: "6px"
                }}>
                    {title}
                </p>
                <p style={{
                    fontSize: "28px", // Increased from 22px
                    fontWeight: "700",
                    color: accentColor,
                    fontFamily: "JetBrains Mono", // Kept JetBrains Mono
                    lineHeight: 1,
                    whiteSpace: "nowrap"
                }}>
                    {value}
                </p>
            </div>

            {/* Ícono derecho */}
            <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: `${accentColor}15`, // opacity ~10-15%
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0
            }}>
                <Icon size={20} color={accentColor} strokeWidth={1.8} />
            </div>
        </div>
    );
};

export default KPICard;
