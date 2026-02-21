
import React from 'react';
import { BarChart3 } from 'lucide-react';

const ChartCard = ({ title, borderColor, children, isLoading }) => {
    return (
        <div style={{
            background: "white",
            borderRadius: "16px",
            padding: "20px 24px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
            borderTop: `3px solid ${borderColor}`,
            height: "100%",
            display: "flex",
            flexDirection: "column"
        }}>
            <p style={{
                fontSize: "11px",
                fontWeight: "700",
                letterSpacing: "0.1em",
                color: "#94a3b8",
                textTransform: "uppercase",
                fontFamily: "JetBrains Mono",
                marginBottom: "16px",
                display: "flex",
                alignItems: "center",
                gap: "8px"
            }}>
                <span style={{
                    width: "4px",
                    height: "16px",
                    borderRadius: "2px",
                    background: borderColor,
                    display: "inline-block"
                }} />
                {title}
            </p>

            <div className="flex-1 min-h-0 relative">
                {isLoading ? (
                    <div className="absolute inset-0 animate-pulse bg-slate-50 rounded-lg flex items-center justify-center">
                        <BarChart3 className="text-slate-200 animate-bounce" size={32} />
                    </div>
                ) : children}
            </div>
        </div>
    );
};

export default ChartCard;
