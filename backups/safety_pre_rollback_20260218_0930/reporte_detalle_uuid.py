import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import json
from utils_ui import render_detalle_uuid_inline

def mostrar_detalle_uuid(df, df_conceptos=None, nivel="premium", z_threshold=2.5):
    """
    Controlador principal para el reporte Detalle UUID.
    Soporta niveles desde básico hasta ultra-premium.
    """
    if df.empty:
        st.info("No hay datos disponibles para los filtros seleccionados.")
        return

    st.markdown('<div class="section-header">REPORTE AVANZADO: DETALLE UUID (PHD EDITION)</div>', unsafe_allow_html=True)

    if nivel == "basico":
        mostrar_tabla_basica(df)
    elif nivel == "mejorado_1":
        mostrar_tabla_mejorada_v1(df)
    elif nivel == "mejorado_2":
        mostrar_tabla_mejorada_v2(df, df_conceptos)
    elif nivel == "premium":
        mostrar_analisis_premium_v4(df, df_conceptos, z_threshold)

def mostrar_tabla_basica(df):
    """Nivel 1: Tabla interactiva básica con exportación."""
    st.subheader("Vista Transaccional Básica")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name='detalle_uuid_basico.csv',
        mime='text/csv',
    )

def mostrar_tabla_mejorada_v1(df):
    """Nivel 2: Tabla con buscadores y filtros integrados."""
    st.subheader("Búsqueda y Exploración Dinámica")
    
    # Buscador Global
    search_query = st.text_input("🔍 Buscar por UUID, RFC o Nombre...", "")
    
    if search_query:
        # Búsqueda simple en todas las columnas string
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        df_display = df[mask]
    else:
        df_display = df

    st.write(f"Mostrando {len(df_display)} registros de {len(df)}.")
    st.dataframe(df_display, use_container_width=True)

def mostrar_tabla_mejorada_v2(df, df_conceptos=None):
    """Nivel 3: Drill-down y filtros laterales."""
    st.subheader("Explorador de Conceptos (Drill-down)")
    
    # Buscador Regex
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        regex_search = st.text_input("🔍 Filtro Regex (UUID o Emisor):", "")
    
    if regex_search:
        try:
            mask = df.astype(str).apply(lambda x: x.str.contains(regex_search, case=False, na=False)).any(axis=1)
            df_filtered = df[mask]
        except:
            st.error("Regex inválido.")
            df_filtered = df
    else:
        df_filtered = df

    # Selección para Drill-down
    selected_uuid = st.selectbox("Seleccione un UUID para auditoría profunda:", df_filtered['uuid'].unique() if 'uuid' in df_filtered.columns else [], key="uuid_selector")
    
    if selected_uuid:
        row = df[df['uuid'] == selected_uuid].iloc[0]
        st.markdown(f'<div class="section-header">AUDITORÍA DE DOCUMENTO: {selected_uuid}</div>', unsafe_allow_html=True)
        render_invoice_premium_html(row, df_conceptos)

    st.markdown("---")
    st.dataframe(df_filtered, use_container_width=True)

def mostrar_analisis_premium_v4(df, df_conceptos=None, z_threshold=2.5):
    """Nivel 4: Ultra Premium - Analítica de Fraude y Desviaciones."""
    
    # 1. Indicadores de Inteligencia Fiscal
    st.markdown('<div class="section-header">AUDITORÍA ALGORÍTMICA (FRAUDE Y RIESGO)</div>', unsafe_allow_html=True)
    
    # Cálculo de Z-Score para detectar montos anómalos
    if 'total' in df.columns and len(df) > 1:
        mean_val = df['total'].mean()
        std_val = df['total'].std()
        if std_val > 0:
            df['z_score'] = (df['total'] - mean_val) / std_val
        else:
            df['z_score'] = 0
            
        outliers = df[df['z_score'].abs() > z_threshold]
    else:
        outliers = pd.DataFrame()

    # Layout de 3 columnas para KPIs de riesgo
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total UUIDs", f"{len(df):,}")
    with k2:
        st.metric("Desviación Media", f"${df['total'].std():,.2f}" if 'total' in df.columns else "$0.00")
    with k3:
        st.metric("Alertas Críticas", f"{len(outliers)}", delta="Outliers detectados", delta_color="inverse")

    # 2. Gráfico de Dispersión de Riesgo (Outliers)
    st.markdown("---")
    st.subheader("Mapa de Calor de Desviaciones (Z-Score)")
    
    if 'total' in df.columns and 'fecha_emision' in df.columns:
        fig = px.scatter(
            df, 
            x='fecha_emision', 
            y='total',
            color=df['z_score'].abs(),
            size=df['total'].abs(),
            hover_data=['uuid', 'emisor_nombre', 'z_score'],
            title="Detección de Anomalías por Monto y Tiempo",
            template="plotly_white",
            color_continuous_scale="Reds"
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="black")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 3. Banner de Alertas Inteligentes
    if not outliers.empty:
        st.warning(f"⚠️ Se han detectado {len(outliers)} transacciones con montos estadísticamente improbables (Z-Score > 2.5).")
        with st.expander("Ver lista de transacciones marcadas para auditoría:"):
            st.table(outliers[['uuid', 'emisor_nombre', 'total', 'z_score']].head(10))

    # 4. Tabla de Datos Principal (con la lógica original de React si se desea alternar)
    st.markdown("---")
    st.subheader("Explorador Detallado de Transacciones")
    
    # Opción para ver la vista híbrida (React Artifact vs Tablas Modernas)
    tab1, tab2 = st.tabs(["Modern Table", "Original Interactive View"])
    
    with tab1:
        # Buscador avanzado para la tabla
        search = st.text_input("Filtrar tabla principal...", "")
        if search:
            df_disp = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
        else:
            df_disp = df
        st.dataframe(df_disp, use_container_width=True)

    with tab2:
        # Reutilizar el componente React original
        try:
            sel_year = st.session_state.get('sel_year', 2024)
            sel_month = st.session_state.get('sel_month', 1)
            month_labels = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            render_detalle_uuid_inline(df, sel_year, sel_month, month_labels)
        except Exception as e:
            st.error(f"Error al cargar vista interactiva: {e}")

def render_invoice_premium_html(row, df_conceptos):
    """Generates the Corporate HTML Invoice with comma31.2 formatting."""
    
    # Safe concepts filter
    concepts_subset = pd.DataFrame()
    invoice_uuid = row.get('uuid')
    if df_conceptos is not None and pd.notnull(invoice_uuid) and 'uuid' in df_conceptos.columns:
        concepts_subset = df_conceptos[df_conceptos['uuid'] == str(invoice_uuid)]
             
    rows_html = ""
    if not concepts_subset.empty:
        for _, c in concepts_subset.iterrows():
            pu = c.get('valor_unitario', 0)
            imp = c.get('importe', 0)
            rows_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{c.get('cantidad', 1)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{c.get('clave_unidad', 'H87')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{c.get('descripcion', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${pu:,.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${imp:,.2f}</td>
            </tr>
            """
    else:
        rows_html = '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #999;"><i>Sin conceptos detallados disponibles</i></td></tr>'

    html_template = f"""
    <div style="font-family: 'Inter', sans-serif; max-width: 850px; margin: 20px auto; background: #ffffff; color: #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; display: flex; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 1px;">ANÁLISIS DE CFDI</h1>
                <p style="margin: 5px 0 0; opacity: 0.8; font-size: 13px; font-family: 'JetBrains Mono';">UUID: {invoice_uuid}</p>
            </div>
            <div style="text-align: right;">
                <h3 style="margin: 0; font-weight: 700;">{row.get('emisor_nombre', 'N/A')}</h3>
                <p style="margin: 2px 0; font-size: 12px; opacity: 0.9;">RFC: {row.get('emisor_rfc', 'N/A')}</p>
                <p style="margin: 0; font-size: 12px; opacity: 0.7;">{row.get('fecha_emision', 'N/A')}</p>
            </div>
        </div>
        
        <div style="padding: 25px; border-bottom: 1px solid #f1f5f9;">
            <p style="margin: 0; color: #764ba2; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Cliente Receptor</p>
            <h2 style="margin: 5px 0 0; font-size: 18px; color: #1e293b;">{row.get('receptor_nombre', 'N/A')}</h2>
            <p style="margin: 2px 0; font-size: 13px; color: #64748b;">RFC: {row.get('receptor_rfc', 'N/A')}</p>
        </div>

        <div style="padding: 20px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background: #f8fafc; color: #475569;">
                        <th style="padding: 12px; border-bottom: 2px solid #e2e8f0; text-align: center;">CANT</th>
                        <th style="padding: 12px; border-bottom: 2px solid #e2e8f0; text-align: center;">UNIDAD</th>
                        <th style="padding: 12px; border-bottom: 2px solid #e2e8f0; text-align: left;">DESCRIPCIÓN</th>
                        <th style="padding: 12px; border-bottom: 2px solid #e2e8f0; text-align: right;">P. UNITARIO</th>
                        <th style="padding: 12px; border-bottom: 2px solid #e2e8f0; text-align: right;">IMPORTE</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>

        <div style="padding: 0 20px 30px; display: flex; justify-content: flex-end;">
            <table style="width: 300px; font-size: 14px; border-collapse: collapse;">
                <tr><td style="padding: 10px; text-align: right; color: #64748b;">Subtotal:</td><td style="padding: 10px; text-align: right; font-weight: 600;">${row.get('subtotal', 0):,.2f}</td></tr>
                <tr><td style="padding: 10px; text-align: right; color: #64748b;">IVA (16%):</td><td style="padding: 10px; text-align: right; font-weight: 600;">${row.get('calc_iva', 0):,.2f}</td></tr>
                <tr style="border-top: 2px solid #764ba2; font-size: 18px;"><td style="padding: 15px; text-align: right; font-weight: 800; color: #764ba2;">TOTAL:</td><td style="padding: 15px; text-align: right; font-weight: 800; color: #764ba2;">${row.get('total', 0):,.2f}</td></tr>
            </table>
        </div>
        
        <div style="background: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #f1f5f9;">
            REPRESENTACIÓN IMPRESA DE CFDI V4.0 // KONIA INTELLIGENCE
        </div>
    </div>
    """
    st.components.v1.html(html_template, height=700, scrolling=True)
