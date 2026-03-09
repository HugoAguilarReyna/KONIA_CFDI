"""
Demo Standalone: Matriz Fiscal + Detalle Inteligente

Ejecutar: streamlit run demo_matriz_detalle.py

Este módulo demuestra las nuevas funciones sin modificar el dashboard principal.
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

st.set_page_config(page_title="Demo Matriz + Detalle", layout="wide")

# ==================== FUNCIONES ====================

def load_matriz_fiscal_aggregated(company_id, mes_ant, mes_act):
    """Carga matriz fiscal agregada desde BigQuery"""
    load_dotenv(override=True)
    bq_project = os.getenv("BQ_PROJECT_ID")
    
    if not bq_project:
        st.error("BQ_PROJECT_ID no configurado")
        return pd.DataFrame()
    
    try:
        client = bigquery.Client(project=bq_project)
        dataset = f"{bq_project}.{os.getenv('BQ_DATASET_ID', 'csmonitor')}"
        company_id_bq = int(os.getenv("BQ_COMPANY_ID", "2"))
        
        query = f"""
        WITH base_cfdis AS (
            SELECT 
                FORMAT_DATE('%Y-%m', c.fecha_emision) as periodo,
                c.tipo,
                c.metodo_pago,
                CAST(c.total AS FLOAT64) as total,
                rel.tipo_relacion,
                COALESCE(parent.metodo_pago, 'NA') as metodo_padre
            FROM `{dataset}.public_cfdis` c
            LEFT JOIN `{dataset}.public_cfdi_relacionados` rel ON c.id = rel.cfdi_id
            LEFT JOIN `{dataset}.public_cfdis` parent ON rel.uuid_relacionado = parent.uuid
            WHERE FORMAT_DATE('%Y-%m', c.fecha_emision) IN ('{mes_ant}', '{mes_act}')
              AND c.company_id = {company_id_bq}
              AND c.estatus = 'vigente'
        ),
        clasificados AS (
            SELECT 
                periodo,
                CASE 
                    WHEN tipo = 'I' AND metodo_pago IN ('PUE', 'PPD') THEN metodo_pago
                    WHEN tipo = 'E' AND metodo_padre IN ('PUE', 'PPD') THEN metodo_padre
                    WHEN tipo = 'E' AND metodo_pago IN ('PUE', 'PPD') THEN metodo_pago
                    ELSE 'OTROS'
                END as segmento,
                CASE 
                    WHEN tipo = 'I' AND COALESCE(tipo_relacion, 'NA') NOT IN ('02') THEN   '1. (+) Total Facturado'
                    WHEN tipo = 'E' AND tipo_relacion = '01' THEN '2. (-) Notas de Crédito (01)'
                    WHEN tipo = 'I' AND tipo_relacion = '02' THEN '3. (+) Nota de Débito (02)'
                    WHEN tipo = 'E' AND tipo_relacion = '03' THEN '4. (-) Devoluciones (03)'
                    WHEN tipo_relacion IN ('05', '06') THEN '6. Traslado de mercancía (05,06)'
                    WHEN tipo = 'E' AND tipo_relacion = '07' THEN '7. (-) Anticipo (07)'
                    WHEN tipo = 'I' THEN '1. (+) Total Facturado'
                    WHEN tipo = 'E' THEN '2. (-) Notas de Crédito (01)'
                    ELSE 'Otros'
                END as concepto_financiero,
                CASE 
                    WHEN tipo = 'I' AND COALESCE(tipo_relacion, 'NA') NOT IN ('02') THEN total
                    WHEN tipo = 'E' AND tipo_relacion = '01' THEN -total
                    WHEN tipo = 'I' AND tipo_relacion = '02' THEN total
                    WHEN tipo = 'E' AND tipo_relacion = '03' THEN -total
                    WHEN tipo_relacion IN ('05', '06') THEN 0.0
                    WHEN tipo = 'E' AND tipo_relacion = '07' THEN -total
                    WHEN tipo = 'I' THEN total
                    WHEN tipo = 'E' THEN -total
                    ELSE 0.0
                END as monto_real
            FROM base_cfdis
        )
        SELECT 
            segmento,
            concepto_financiero,
            SUM(CASE WHEN periodo = '{mes_ant}' THEN monto_real ELSE 0 END) as mes_anterior,
            SUM(CASE WHEN periodo = '{mes_act}' THEN monto_real ELSE 0 END) as mes_actual
        FROM clasificados
        GROUP BY segmento, concepto_financiero
        ORDER BY segmento, concepto_financiero
        """
        
        df_matriz = client.query(query).to_dataframe()
        
        if not df_matriz.empty:
            df_matriz['delta_pct'] = ((df_matriz['mes_actual'] - df_matriz['mes_anterior']) / 
                                      df_matriz['mes_anterior'].replace(0, 1)) * 100
            df_matriz['tendencia'] = df_matriz['delta_pct'].apply(
                lambda x: '🔺' if x > 5 else ('🔻' if x < -5 else '➖')
            )
        
        return df_matriz
        
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def load_cfdi_detalle_filtered(company_id, selected_period, filter_preset='todos', search_query=None, max_rows=500):
    """Carga detalles con filtros inteligentes"""
    load_dotenv(override=True)
    bq_project = os.getenv("BQ_PROJECT_ID")
    
    if not bq_project:
        st.error("BQ_PROJECT_ID no configurado")
        return pd.DataFrame()
    
    try:
        client = bigquery.Client(project=bq_project)
        dataset = f"{bq_project}.{os.getenv('BQ_DATASET_ID', 'csmonitor')}"
        company_id_bq = int(os.getenv("BQ_COMPANY_ID", "2"))
        
        base_select = f"""
        SELECT 
            c.uuid,
            c.tipo,
            c.metodo_pago,
            c.fecha_emision,
            CAST(c.total AS FLOAT64) as total,
            e.rfc as emisor_rfc,
            r.rfc as receptor_rfc
        FROM `{dataset}.public_cfdis` c
        LEFT JOIN `{dataset}.public_cfdi_emisors` e ON c.emisor_id = e.id
        LEFT JOIN `{dataset}.public_cfdi_receptors` r ON c.receptor_id = r.id
        WHERE FORMAT_DATE('%Y-%m', c.fecha_emision) = '{selected_period}'
          AND c.company_id = {company_id_bq}
          AND c.estatus = 'vigente'
        """
        
        if filter_preset == 'altos_montos':
            where_clause = "AND CAST(c.total AS FLOAT64) > 100000"
        elif filter_preset == 'anomalias':
            where_clause = "AND (CAST(c.total AS FLOAT64) < 500 OR DATE_DIFF(CURRENT_DATE(), c.fecha_emision, DAY) > 90)"
        else:
            where_clause = ""
        
        query = base_select + where_clause + f" ORDER BY c.fecha_emision DESC LIMIT {max_rows}"
        
        df_detalle = client.query(query).to_dataframe()
        return df_detalle
        
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ==================== UI ====================

st.title("󠁧󠁧󠁧󠀠📊 Demo: Matriz Fiscal + Detalle Inteligente")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    company_id = 2
    mes_ant = st.text_input("Mes Anterior (YYYY-MM)", "2026-01")
    mes_act = st.text_input("Mes Actual (YYYY-MM)", "2026-02")
    
    st.markdown("---")
    
    detail_preset = st.selectbox(
        "Filtro Detalles",
        ["Todos", "Altos Montos", "Anomalías"]
    )
    max_rows = st.slider("Max Registros", 100, 1000, 500, 100)

# NIVEL 1: MATRIZ FISCAL
st.markdown("## 📈 Nivel 1: Matriz Fiscal Agregada")
with st.spinner("Cargando matriz..."):
    df_matriz = load_matriz_fiscal_aggregated(company_id, mes_ant, mes_act)

if not df_matriz.empty:
    st.dataframe(df_matriz, use_container_width=True)
    st.success(f"✅ {len(df_matriz)} filas cargadas")
else:
    st.warning("Sin datos")

st.markdown("---")

# NIVEL 2: DETALLE FILTRADO
st.markdown("## 🔍 Nivel 2: Detalle UUID")
preset_map = {"Todos": "todos", "Altos Montos": "altos_montos", "Anomalías": "anomalias"}

with st.spinner(f"Cargando detalles ({detail_preset})..."):
    df_detalle = load_cfdi_detalle_filtered(
        company_id, 
        mes_act, 
        preset_map[detail_preset], 
        max_rows=max_rows
    )

if not df_detalle.empty:
    st.dataframe(df_detalle, use_container_width=True)
    st.success(f"✅ {len(df_detalle)} registros cargados")
    
    # Expandir detalles
    st.markdown("### Expanders de prueba")
    for i, row in df_detalle.head(5).iterrows():
        with st.expander(f"🔍 {row['uuid'][:16]}..."):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", f"${row['total']:,.2f}")
            with col2:
                st.metric("Tipo", row['tipo'])
            with col3:
                st.metric("Método", row['metodo_pago'])
else:
    st.warning("Sin datos")
