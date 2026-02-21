import React from 'react';
import Plot from 'react-plotly.js';
import { ResponsiveContainer } from 'recharts';

const ChartWrapper = ({ type = 'plotly', data, layout, config, isLoading, height = 400, children }) => {

    if (isLoading) {
        return (
            <div className="glass-card w-full p-4 animate-pulse flex flex-col items-center justify-center" style={{ height }}>
                <div className="w-full h-full bg-slate-100 rounded-lg flex items-center justify-center">
                    <span className="text-slate-300 font-medium">Cargando Gráfica...</span>
                </div>
            </div>
        );
    }

    if (type === 'plotly') {
        return (
            <div className="glass-card w-full p-2 h-full rounded-xl overflow-hidden shadow-sm">
                <Plot
                    data={data}
                    layout={{
                        autosize: true,
                        height: height,
                        margin: { l: 40, r: 20, t: 30, b: 40 },
                        showlegend: true,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { family: 'Inter, sans-serif', color: '#64748b' },
                        xaxis: {
                            gridcolor: '#f1f5f9',
                            zerolinecolor: '#f1f5f9',
                        },
                        yaxis: {
                            gridcolor: '#f1f5f9',
                            zerolinecolor: '#f1f5f9',
                        },
                        ...layout
                    }}
                    config={{
                        responsive: true,
                        displayModeBar: false,
                        ...config
                    }}
                    style={{ width: '100%', height: '100%' }}
                    useResizeHandler={true}
                />
            </div>
        );
    }

    if (type === 'recharts') {
        return (
            <div className="glass-card w-full p-4 h-full rounded-xl" style={{ height }}>
                <ResponsiveContainer width="100%" height="100%">
                    {children}
                </ResponsiveContainer>
            </div>
        );
    }

    return null;
};

export default ChartWrapper;
