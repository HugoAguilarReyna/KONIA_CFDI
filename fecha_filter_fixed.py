"""
FILTRO DE FECHA CORREGIDO
Solo usa componentes de Streamlit, sin HTML que rompa el layout
"""

import streamlit as st
from datetime import datetime

def filtro_fecha_con_calendario(
    label: str = "Período Fiscal",
    year_min: int = 2020,
    year_max: int = 2026,
    df_tiempo = None
):
    """
    Filtro de fecha CORRECTO para sidebar.
    
    Retorna:
    - Dict con 'year' y 'month'
    """
    
    # Inicializar estado
    if "filter_year" not in st.session_state:
        st.session_state.filter_year = datetime.now().year
    if "filter_month" not in st.session_state:
        st.session_state.filter_month = datetime.now().month
    
    # Título Principal
    st.write(f"**{label}**")
    st.write("") # Salto de línea para separación
    
    # 1. MODO DE SELECCIÓN
    modo = st.radio("Modo", options=["Mes Único", "Rango de Meses"], horizontal=True, label_visibility="collapsed")
    
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    if modo == "Mes Único":
        # Layout para Mes Único
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Año**")
            
            if df_tiempo is not None and not df_tiempo.empty:
                year_options = sorted(df_tiempo['anio'].unique().tolist())
            else:
                year_options = list(range(year_min, year_max + 1))
            
            # Ensure session state is valid for options
            if st.session_state.filter_year not in year_options:
                st.session_state.filter_year = year_options[-1]
            
            year = st.selectbox(
                "Año",
                options=year_options,
                index=year_options.index(st.session_state.filter_year),
                key="year_select_key",
                label_visibility="collapsed"
            )
            st.session_state.filter_year = year
        
        with col2:
            st.write("**Mes**")
            
            if df_tiempo is not None and not df_tiempo.empty:
                # Filter months available for the selected year
                month_options = sorted(df_tiempo[df_tiempo['anio'] == year]['mes'].unique().tolist())
            else:
                month_options = list(range(1, 13))
            
            # Ensure session state is valid for options
            if st.session_state.filter_month not in month_options:
                st.session_state.filter_month = month_options[0]

            month_num = st.selectbox(
                "Mes",
                options=month_options,
                format_func=lambda x: months[x - 1],
                index=month_options.index(st.session_state.filter_month),
                key="month_select_key",
                label_visibility="collapsed"
            )
            st.session_state.filter_month = month_num
        
        st.caption(f"✓ Período: {months[month_num - 1]} {year}")
        return {
            "mode": "single",
            "year": year,
            "month": month_num
        }

    else:
        # Layout para Rango
        st.write("**Desde**")
        c1, c2 = st.columns(2)
        
        if df_tiempo is not None and not df_tiempo.empty:
             year_options = sorted(df_tiempo['anio'].unique().tolist())
        else:
             year_options = list(range(year_min, year_max + 1))

        with c1:
            st.write("**Año**")
            y_start = st.selectbox("A1", options=year_options, index=year_options.index(st.session_state.get('filter_year', year_options[-1])) if st.session_state.get('filter_year') in year_options else 0, key="y_start", label_visibility="collapsed")
        with c2:
            st.write("**Mes**")
            if df_tiempo is not None and not df_tiempo.empty:
                m_start_opts = sorted(df_tiempo[df_tiempo['anio'] == y_start]['mes'].unique().tolist())
            else:
                m_start_opts = list(range(1, 13))
            m_start = st.selectbox("M1", options=m_start_opts, format_func=lambda x: months[x - 1], index=0, key="m_start", label_visibility="collapsed")
        
        st.write("**Hasta**")
        c3, c4 = st.columns(2)
        with c3:
            st.write("**Año**")
            y_end = st.selectbox("A2", options=year_options, index=year_options.index(st.session_state.get('filter_year', year_options[-1])) if st.session_state.get('filter_year') in year_options else 0, key="y_end", label_visibility="collapsed")
        with c4:
            st.write("**Mes**")
            if df_tiempo is not None and not df_tiempo.empty:
                m_end_opts = sorted(df_tiempo[df_tiempo['anio'] == y_end]['mes'].unique().tolist())
            else:
                m_end_opts = list(range(1, 13))
            m_end = st.selectbox("M2", options=m_end_opts, format_func=lambda x: months[x - 1], index=m_end_opts.index(st.session_state.filter_month) if st.session_state.filter_month in m_end_opts else 0, key="m_end", label_visibility="collapsed")

        st.caption(f"✓ Rango: {months[m_start-1]} {y_start} a {months[m_end-1]} {y_end}")
        return {
            "mode": "range",
            "start_year": y_start,
            "start_month": m_start,
            "end_year": y_end,
            "end_month": m_end
        }
