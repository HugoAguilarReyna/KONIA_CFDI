import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# =============================================================================
# DATA FETCHING (MONGODB)
# =============================================================================

@st.cache_data(ttl=3600)
def get_traceable_uuids(_db_fiscal, company_id=2):
    """
    Returns a list of unique UUIDs that have traceability events, with a "TODOS" option.
    """
    try:
        uuids = _db_fiscal.trazabilidad_uuid.distinct("uuid_raiz", {"company_id": company_id})
        sorted_uuids = sorted([u for u in uuids if u])
        return ["TODOS"] + sorted_uuids
    except Exception as e:
        st.error(f"Error al obtener UUIDs de trazabilidad: {e}")
        return []

@st.cache_data(ttl=3600)
def get_uuid_events(_db_fiscal, uuid_raiz, company_id=2):
    """
    Returns a DataFrame with all events for a specific UUID or all UUIDs if "TODOS" is selected.
    """
    try:
        if uuid_raiz == "TODOS":
            query = {"company_id": company_id}
        else:
            query = {"uuid_raiz": uuid_raiz, "company_id": company_id}
            
        docs = list(_db_fiscal.trazabilidad_uuid.find(query, {"_id": 0}).sort("fecha", 1))
        if not docs:
            return pd.DataFrame()
        
        df = pd.DataFrame(docs)
        # Ensure date is datetime using robust ISO8601 parsing
        df['fecha'] = pd.to_datetime(df['fecha'], format='ISO8601', errors='coerce')
        # Sort again after conversion just in case, and drop any rows that failed parsing
        df = df.dropna(subset=['fecha']).sort_values('fecha')
        return df
    except Exception as e:
        st.error(f"Error al obtener eventos del UUID {uuid_raiz}: {e}")
        return pd.DataFrame()

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_trazabilidad_tab(db_fiscal, company_id=2):
    """
    Main function to render the Traceability UI.
    """
    # 0. Inject Global styles + Local Overrides
    st.markdown("""
        <style>
        /* Replicate Premium Section Header */
        .premium-section-header {
            font-family: 'JetBrains Mono', monospace;
            font-size: 16px;
            color: var(--color-primary);
            border-left: 4px solid var(--color-primary);
            padding: 8px 15px;
            margin: 25px 0 15px 0;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
            display: flex;
            align-items: center;
        }
        
        /* Premium Card Style */
        .premium-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-xl);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--glass-shadow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .premium-card:hover {
            transform: translateY(-2px);
            border-color: var(--color-primary);
        }

        /* KPI Card Extension */
        .kpi-container {
            border-left: 4px solid var(--color-primary);
        }
        
        .kpi-content {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .kpi-label {
            font-family: var(--font-sans);
            font-size: 11px;
            color: var(--text-secondary);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }
        
        .kpi-value {
            font-family: var(--font-sans);
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1;
        }

        .kpi-icon-box {
            padding: 10px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .bg-indigo-premium { background-color: rgba(99, 102, 241, 0.1); color: #6366f1; }
        .bg-emerald-premium { background-color: rgba(16, 185, 129, 0.1); color: #10b981; }
        .bg-amber-premium { background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; }
        .bg-purple-premium { background-color: rgba(168, 85, 247, 0.1); color: #a855f7; }

        .badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    def render_premium_kpi(label, value, icon_svg="", color_class="bg-indigo-premium"):
        st.markdown(f"""
            <div class="premium-card kpi-container">
                <div class="kpi-content">
                    <div>
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value">{value}</div>
                    </div>
                    <div class="kpi-icon-box {color_class}">
                        {icon_svg}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # SVG Icon Mapping
    svgs = {
        "layers": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        "dollar-sign": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
        "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
    }

    # 1. Header & Selector
    col_sel, col_empty = st.columns([2, 1])
    with col_sel:
        available_uuids = get_traceable_uuids(db_fiscal, company_id)
        if not available_uuids:
            st.info("No se encontraron UUIDs con trazabilidad disponible.")
            return

        selected_uuid = st.selectbox(
            "🔍 Selecciona un UUID para ver su trazabilidad",
            options=available_uuids,
            index=0,
            key="trace_uuid_selector"
        )

    if not selected_uuid:
        return

    # 2. Data Loading
    with st.spinner(f"Cargando trazabilidad para {selected_uuid[:8]}..."):
        df_events = get_uuid_events(db_fiscal, selected_uuid, company_id)

    if df_events.empty:
        st.warning(f"No hay eventos registrados para el filtro seleccionado.")
        return

    # 3. Filters
    min_date = df_events['fecha'].min().date()
    max_date = df_events['fecha'].max().date()

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        date_from = st.date_input("Desde", min_date, min_value=min_date, max_value=max_date)
    with c2:
        date_to = st.date_input("Hasta", max_date, min_value=min_date, max_value=max_date)
    with c3:
        st.write("") # Spacer
        st.write("")
        # Local Filter for UI elements (not for global balance)
        df_filtered = df_events[
            (df_events['fecha'].dt.date >= date_from) & 
            (df_events['fecha'].dt.date <= date_to)
        ].copy()

    # 4. KPIs
    total_eventos = len(df_events)
    # If "TODOS", the saldo_acumulado from the last row might be misleading if it's not a running global sum
    # but based on the schema, it's per-event. 
    # Let's show the last known saldo or a sum if "TODOS"? 
    # Usually users want to see the sum of current balances if TODOS.
    if selected_uuid == "TODOS":
        # Get the latest event for each uuid_raiz to sum current balances
        latest_balances = df_events.sort_values('fecha').groupby('uuid_raiz').tail(1)
        saldo_display = latest_balances['saldo_acumulado'].sum()
        kpi_label = "💰 Saldo Total (Suma)"
    else:
        saldo_display = df_events.iloc[-1]['saldo_acumulado']
        kpi_label = "💰 Saldo Actual"

    primer_evento = df_events['fecha'].min().strftime('%Y-%m-%d')
    ultimo_evento = df_events['fecha'].max().strftime('%Y-%m-%d')

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_premium_kpi("Total Eventos", f"{total_eventos:,}", icon_svg=svgs["layers"], color_class="bg-indigo-premium")
    with k2:
        render_premium_kpi(kpi_label.replace("💰 ", ""), f"${saldo_display:,.2f}", icon_svg=svgs["dollar-sign"], color_class="bg-emerald-premium")
    with k3:
        render_premium_kpi("Primer Evento", primer_evento, icon_svg=svgs["calendar"], color_class="bg-amber-premium")
    with k4:
        render_premium_kpi("Último Evento", ultimo_evento, icon_svg=svgs["clock"], color_class="bg-purple-premium")

    # 5. Evolution Chart
    st.markdown('<div class="premium-section-header">📈 Evolución del Saldo</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        fig = go.Figure()
    
    if selected_uuid == "TODOS":
        # Show points for each event, maybe colored by UUID or just a global timeline
        fig.add_trace(go.Scatter(
            x=df_events['fecha'],
            y=df_events['saldo_acumulado'],
            mode='markers',
            name='Eventos Globales',
            marker=dict(size=6, color='#6366f1', opacity=0.6),
            hovertemplate="<b>UUID:</b> %{text}<br><b>Fecha:</b> %{x}<br><b>Saldo:</b> $%{y:,.2f}<extra></extra>",
            text=df_events['uuid_raiz']
        ))
    else:
        # Area Chart for single UUID
        fig.add_trace(go.Scatter(
            x=df_events['fecha'],
            y=df_events['saldo_acumulado'],
            mode='lines+markers',
            name='Saldo Acumulado',
            line=dict(color='#6366f1', width=3),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.1)',
            marker=dict(size=8, color='#6366f1', symbol='circle'),
            hovertemplate="<b>Fecha:</b> %{x}<br><b>Saldo:</b> $%{y:,.2f}<extra></extra>"
        ))

    # Add indicators for filtered range
    fig.add_vrect(
        x0=pd.to_datetime(date_from), x1=pd.to_datetime(date_to),
        fillcolor="rgba(168, 85, 247, 0.05)", opacity=0.5,
        layer="below", line_width=0,
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=0),
        height=350,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=True, zerolinecolor='rgba(255,255,255,0.1)'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. Event Table
    st.markdown('<div class="premium-section-header">📋 Historial de Eventos</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    
    # Prepare data for display
    display_df = df_filtered.copy()
    display_df['fecha_str'] = display_df['fecha'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['uuid_rel_short'] = display_df['uuid_relacionado'].apply(lambda x: f"{str(x)[:8]}..." if x and str(x) != 'None' else "—")
    
    cols_to_show = ['fecha_str', 'tipo_relacion', 'concepto', 'uuid_rel_short', 'monto', 'saldo_acumulado']
    column_config = {
        "fecha_str": "Fecha/Hora",
        "tipo_relacion": st.column_config.TextColumn("Tipo Relación"),
        "concepto": "Concepto",
        "uuid_rel_short": "UUID Relacionado",
        "monto": st.column_config.NumberColumn("Monto", format="$%.2f"),
        "saldo_acumulado": st.column_config.NumberColumn("Saldo Acumulado", format="$%.2f"),
    }

    if selected_uuid == "TODOS":
        display_df['uuid_raiz_short'] = display_df['uuid_raiz'].apply(lambda x: f"{str(x)[:8]}...")
        cols_to_show.insert(1, 'uuid_raiz_short')
        column_config["uuid_raiz_short"] = "UUID Original"

    # Advanced Table Config
    st.dataframe(
        display_df[cols_to_show],
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. Export
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar eventos filtrados (CSV)",
        data=csv,
        file_name=f"trazabilidad_{selected_uuid[:8]}.csv",
        mime='text/csv',
    )
